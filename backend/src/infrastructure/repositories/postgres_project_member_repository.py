"""Triển khai PostgreSQL Repository cho thực thể ProjectMember."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.project.entities import ProjectMember
from src.domain.project.repository import IProjectMemberRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.project_member_mapper import ProjectMemberMapper
from src.infrastructure.database.models.project_member import ProjectMemberModel
from typing_extensions import override


class PostgresProjectMemberRepository(IProjectMemberRepository):
    """Triển khai IProjectMemberRepository sử dụng SQLAlchemy AsyncSession và ProjectMemberMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    async def get_by_id(self, entity_id: EntityID) -> ProjectMember | None:
        """Lấy thành viên dự án theo ID."""
        stmt = select(ProjectMemberModel).where(ProjectMemberModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProjectMemberMapper.to_domain(model) if model else None

    @override
    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        """Danh sách thành viên thuộc một dự án."""
        stmt = select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [ProjectMemberMapper.to_domain(m) for m in models]

    @override
    async def is_member(self, project_id: EntityID, user_id: EntityID) -> bool:
        stmt = select(ProjectMemberModel.id).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @override
    async def save(self, entity: ProjectMember) -> ProjectMember:
        """Lưu (tạo mới hoặc cập nhật) thực thể ProjectMember."""
        stmt = select(ProjectMemberModel).where(ProjectMemberModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = ProjectMemberMapper.update_model(existing_model, entity)
        else:
            model = ProjectMemberMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return ProjectMemberMapper.to_domain(model)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể ProjectMember theo ID."""
        stmt = select(ProjectMemberModel).where(ProjectMemberModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
