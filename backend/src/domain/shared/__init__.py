"""Module chứa các thành phần dùng chung cho tầng Domain."""

from src.domain.shared.entity import BaseEntity
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject

__all__: list[str] = [
    "BaseEntity",
    "BaseValueObject",
    "EntityID",
    "IBaseRepository",
]
