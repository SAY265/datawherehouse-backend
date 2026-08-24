"""Triển khai PostgreSQL Repository cho thực thể Project."""

from config import get_settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.logging import get_logger
from src.domain.project.entities import Project
from src.domain.project.repository import IProjectRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.project_mapper import ProjectMapper
from src.infrastructure.database.models.project import ProjectModel
from src.infrastructure.repositories.in_memory_store import InMemoryStore
from typing_extensions import override

logger = get_logger(__name__)


class PostgresProjectRepository(IProjectRepository):
    """Triển khai IProjectRepository sử dụng SQLAlchemy AsyncSession với In-Memory Fallback."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session
        self._mem = InMemoryStore.get_instance()
        self._allow_memory_fallback = get_settings().app_env != "production"

    @override
    async def get_by_id(self, entity_id: EntityID) -> Project | None:
        """Lấy dự án theo ID."""
        try:
            stmt = select(ProjectModel).where(ProjectModel.id == entity_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return ProjectMapper.to_domain(model) if model else None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for get_project_by_id: %s", exc)
            return self._mem.get_project_by_id(entity_id)

    @override
    async def list_by_user(self, user_id: EntityID) -> list[Project]:
        """Lấy danh sách dự án sở hữu bởi người dùng."""
        try:
            stmt = select(ProjectModel).where(ProjectModel.user_id == user_id)
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            return [ProjectMapper.to_domain(m) for m in models]
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for list_projects_by_user: %s", exc)
            return self._mem.list_projects_by_user(user_id)

    @override
    async def save(self, entity: Project) -> Project:
        """Lưu (tạo mới hoặc cập nhật) thực thể Project."""
        if self._allow_memory_fallback:
            self._mem.save_project(entity)
        try:
            stmt = select(ProjectModel).where(ProjectModel.id == entity.id)
            result = await self._session.execute(stmt)
            existing_model = result.scalar_one_or_none()

            if existing_model:
                model = ProjectMapper.update_model(existing_model, entity)
            else:
                model = ProjectMapper.to_model(entity)
                self._session.add(model)

            await self._session.flush()
            return ProjectMapper.to_domain(model)
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, project saved to in-memory store: %s", exc)
            return entity

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể Project theo ID."""
        if self._allow_memory_fallback:
            self._mem.delete_project(entity_id)
        try:
            stmt = select(ProjectModel).where(ProjectModel.id == entity_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return False
            await self._session.delete(model)
            await self._session.flush()
            return True
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, deleted project from in-memory store: %s", exc)
            return True
