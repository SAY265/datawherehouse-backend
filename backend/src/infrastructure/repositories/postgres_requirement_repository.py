"""Triển khai PostgreSQL Repository cho thực thể Requirement."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.requirement.entities import Requirement
from src.domain.requirement.repository import IRequirementRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.requirement_mapper import RequirementMapper
from src.infrastructure.database.models.requirement import RequirementModel
from typing_extensions import override


class PostgresRequirementRepository(IRequirementRepository):
    """Triển khai IRequirementRepository sử dụng SQLAlchemy AsyncSession và RequirementMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    async def get_by_id(self, entity_id: EntityID) -> Requirement | None:
        """Lấy yêu cầu theo ID."""
        stmt = select(RequirementModel).where(RequirementModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return RequirementMapper.to_domain(model) if model else None

    @override
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        """Lấy danh sách yêu cầu thuộc một dự án."""
        stmt = select(RequirementModel).where(RequirementModel.project_id == project_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [RequirementMapper.to_domain(m) for m in models]

    @override
    async def save(self, entity: Requirement) -> Requirement:
        """Lưu (tạo mới hoặc cập nhật) thực thể Requirement."""
        stmt = select(RequirementModel).where(RequirementModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = RequirementMapper.update_model(existing_model, entity)
        else:
            model = RequirementMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return RequirementMapper.to_domain(model)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể Requirement theo ID."""
        stmt = select(RequirementModel).where(RequirementModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
