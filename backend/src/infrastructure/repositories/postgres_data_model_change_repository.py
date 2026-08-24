"""Triển khai PostgreSQL Repository cho thực thể DataModelChange."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.data_model.entities import DataModelChange
from src.domain.data_model.repository import IDataModelChangeRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.data_model_change_mapper import (
    DataModelChangeMapper,
)
from src.infrastructure.database.models.data_model_change import DataModelChangeModel
from typing_extensions import override


class PostgresDataModelChangeRepository(IDataModelChangeRepository):
    """Triển khai IDataModelChangeRepository sử dụng AsyncSession và DataModelChangeMapper."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataModelChange | None:
        """Lấy Đề xuất Thay đổi theo ID."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DataModelChangeMapper.to_domain(model) if model else None

    @override
    async def list_by_data_model(self, data_model_id: EntityID) -> list[DataModelChange]:
        """Danh sách các đề xuất thay đổi thuộc một mô hình dữ liệu."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.data_model_id == data_model_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [DataModelChangeMapper.to_domain(m) for m in models]

    @override
    async def save(self, entity: DataModelChange) -> DataModelChange:
        """Lưu (tạo mới hoặc cập nhật) thực thể DataModelChange."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            model = DataModelChangeMapper.update_model(existing_model, entity)
        else:
            model = DataModelChangeMapper.to_model(entity)
            self._session.add(model)

        await self._session.flush()
        return DataModelChangeMapper.to_domain(model)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể DataModelChange theo ID."""
        stmt = select(DataModelChangeModel).where(DataModelChangeModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
