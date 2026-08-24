"""Triển khai PostgreSQL Repository cho thực thể ProjectSession."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.repository import IProjectSessionRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.project_session_mapper import ProjectSessionMapper
from src.infrastructure.database.models.project_session import ProjectSessionModel
from typing_extensions import override


class PostgresAgentSessionRepository(IProjectSessionRepository):
    """Triển khai IProjectSessionRepository sử dụng AsyncSession và ProjectSessionMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    async def get_by_id(self, entity_id: EntityID) -> ProjectSession | None:
        """Lấy Phiên làm việc theo ID."""
        stmt = select(ProjectSessionModel).where(ProjectSessionModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProjectSessionMapper.to_domain(model) if model else None

    @override
    async def list_by_project(self, project_id: EntityID) -> list[ProjectSession]:
        """Danh sách các phiên thuộc một dự án."""
        stmt = select(ProjectSessionModel).where(ProjectSessionModel.project_id == project_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [ProjectSessionMapper.to_domain(m) for m in models]

    @override
    async def save(self, entity: ProjectSession) -> ProjectSession:
        """Lưu (tạo mới hoặc cập nhật) thực thể ProjectSession."""
        stmt = select(ProjectSessionModel).where(ProjectSessionModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = ProjectSessionMapper.update_model(existing_model, entity)
        else:
            model = ProjectSessionMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return ProjectSessionMapper.to_domain(model)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể ProjectSession theo ID."""
        stmt = select(ProjectSessionModel).where(ProjectSessionModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
