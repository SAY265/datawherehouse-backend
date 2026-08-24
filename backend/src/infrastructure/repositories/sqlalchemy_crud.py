"""CRUD SQLAlchemy dùng chung cho các repository theo Domain contract."""

from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID
from src.infrastructure.database.base import Base
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.orm_mapper import OrmMapper

DomainEntity = TypeVar("DomainEntity", bound=BaseEntity)
OrmModel = TypeVar("OrmModel", bound=Base)


class SqlAlchemyCrud(Generic[DomainEntity, OrmModel]):
    """Thực hiện CRUD kỹ thuật, không chứa query nghiệp vụ."""

    def __init__(
        self,
        session: AsyncSession,
        model_type: type[OrmModel],
        mapper: type[OrmMapper[DomainEntity, OrmModel]],
    ) -> None:
        """Khởi tạo CRUD với session, ORM model và mapper tương ứng."""
        self._session = session
        self._model_type = model_type
        self._mapper = mapper

    @translate_database_errors
    async def get_by_id(self, entity_id: EntityID) -> DomainEntity | None:
        """Lấy entity theo ID."""
        model = await self._session.get(self._model_type, entity_id)
        return self._mapper.to_domain(model) if model else None

    @translate_database_errors
    async def save(self, entity: DomainEntity) -> DomainEntity:
        """Lưu mới hoặc cập nhật entity."""
        model = await self._session.get(self._model_type, entity.id)
        if model is None:
            model = self._mapper.to_model(entity)
            self._session.add(model)
        else:
            self._mapper.update_model(model, entity)
        await self._session.flush()
        return self._mapper.to_domain(model)

    @translate_database_errors
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa entity và trả trạng thái tìm thấy."""
        model = await self._session.get(self._model_type, entity_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
