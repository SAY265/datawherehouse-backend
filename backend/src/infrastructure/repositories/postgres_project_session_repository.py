"""PostgreSQL repository cho thực thể ProjectSession."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.project_session_mapper import ProjectSessionMapper
from src.infrastructure.database.models.project_session import ProjectSessionModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud
from typing_extensions import override


class PostgresProjectSessionRepository(IProjectSessionRepository):
    """Lưu trữ ProjectSession bằng SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = SqlAlchemyCrud(session, ProjectSessionModel, ProjectSessionMapper)

    @override
    @translate_database_errors
    async def get_by_id_for_update(
        self, entity_id: EntityID
    ) -> ProjectSession | None:
        statement = (
            select(ProjectSessionModel)
            .where(ProjectSessionModel.id == entity_id)
            .with_for_update()
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return ProjectSessionMapper.to_domain(model) if model else None

    @override
    async def get_by_id(self, entity_id: EntityID) -> ProjectSession | None:
        """Lấy phiên làm việc theo ID."""
        return await self._crud.get_by_id(entity_id)

    @override
    @translate_database_errors
    async def list_by_project(self, project_id: EntityID) -> list[ProjectSession]:
        """Lấy các phiên làm việc thuộc một dự án."""
        statement = select(ProjectSessionModel).where(ProjectSessionModel.project_id == project_id)
        result = await self._session.execute(statement)
        return [ProjectSessionMapper.to_domain(model) for model in result.scalars().all()]

    @override
    @translate_database_errors
    async def list_by_project_user(
        self, project_id: EntityID, user_id: EntityID
    ) -> list[ProjectSession]:
        """Lấy session của actor, mới cập nhật trước."""
        statement = (
            select(ProjectSessionModel)
            .where(
                ProjectSessionModel.project_id == project_id,
                ProjectSessionModel.user_id == user_id,
            )
            .order_by(ProjectSessionModel.updated_at.desc())
        )
        result = await self._session.execute(statement)
        return [ProjectSessionMapper.to_domain(model) for model in result.scalars().all()]

    @override
    async def save(self, entity: ProjectSession) -> ProjectSession:
        """Lưu mới hoặc cập nhật phiên làm việc."""
        return await self._crud.save(entity)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa phiên làm việc theo ID."""
        return await self._crud.delete(entity_id)
