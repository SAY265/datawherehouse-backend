"""Triển khai PostgreSQL Repository cho thực thể DataModel."""

from config import get_settings
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.logging import get_logger
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.shared.types import EntityID
from src.infrastructure.database.mappers.data_model_mapper import DataModelMapper
from src.infrastructure.database.models.data_model import DataModelModel
from src.infrastructure.repositories.in_memory_store import InMemoryStore
from typing_extensions import override

logger = get_logger(__name__)


class PostgresDataModelRepository(IDataModelRepository):
    """Triển khai IDataModelRepository sử dụng AsyncSession với In-Memory Fallback."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session
        self._mem = InMemoryStore.get_instance()
        self._allow_memory_fallback = get_settings().app_env != "production"

    @override
    async def get_by_id(self, entity_id: EntityID) -> DataModel | None:
        """Lấy Mô hình dữ liệu theo ID."""
        try:
            stmt = select(DataModelModel).where(DataModelModel.id == entity_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return DataModelMapper.to_domain(model) if model else None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for get_data_model_by_id: %s", exc)
            return self._mem.get_data_model_by_id(entity_id)

    @override
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo dự án."""
        try:
            stmt = select(DataModelModel).where(DataModelModel.project_id == project_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return DataModelMapper.to_domain(model) if model else None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for get_by_project_id: %s", exc)
            return self._mem.get_data_model_by_project_id(project_id)

    @override
    async def save(self, entity: DataModel) -> DataModel:
        """Lưu (tạo mới hoặc cập nhật) thực thể DataModel."""
        if self._allow_memory_fallback:
            self._mem.save_data_model(entity)
        try:
            stmt = select(DataModelModel).where(DataModelModel.id == entity.id)
            result = await self._session.execute(stmt)
            existing_model = result.scalar_one_or_none()

            if existing_model:
                model = DataModelMapper.update_model(existing_model, entity)
            else:
                model = DataModelMapper.to_model(entity)
                self._session.add(model)

            await self._session.flush()
            return DataModelMapper.to_domain(model)
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, data model saved to in-memory store: %s", exc)
            return entity

    @override
    async def update_if_revision_matches(self, entity: DataModel, base_revision: int) -> DataModel | None:
        """Cập nhật DBML bằng optimistic locking."""
        try:
            stmt = (
                update(DataModelModel)
                .where(
                    DataModelModel.id == entity.id,
                    DataModelModel.revision == base_revision,
                )
                .values(
                    dbml=entity.dbml,
                    revision=entity.revision,
                    updated_at=entity.updated_at,
                )
                .returning(DataModelModel)
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is not None:
                if self._allow_memory_fallback:
                    self._mem.save_data_model(entity)
                return DataModelMapper.to_domain(model)
            return None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, updating data model in in-memory store: %s", exc)
            return self._mem.update_data_model_if_revision_matches(entity, base_revision)

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể DataModel theo ID."""
        if self._allow_memory_fallback:
            self._mem.delete_data_model(entity_id)
        try:
            stmt = select(DataModelModel).where(DataModelModel.id == entity_id)
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
            logger.warning("Database unavailable, deleted data model from in-memory store: %s", exc)
            return True
