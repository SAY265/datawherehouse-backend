"""Contract nội bộ cho mapper giữa Domain entity và SQLAlchemy model."""

from typing import Protocol, TypeVar

DomainEntity = TypeVar("DomainEntity")
OrmModel = TypeVar("OrmModel")


class OrmMapper(Protocol[DomainEntity, OrmModel]):
    """Mô tả ba phép ánh xạ dùng bởi CRUD repository."""

    @staticmethod
    def to_domain(model: OrmModel) -> DomainEntity: ...

    @staticmethod
    def to_model(entity: DomainEntity) -> OrmModel: ...

    @staticmethod
    def update_model(model: OrmModel, entity: DomainEntity) -> OrmModel: ...
