"""Giao diện Repository cơ sở (IBaseRepository) dùng chung cho tầng Domain."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID

TEntity = TypeVar("TEntity", bound=BaseEntity)


class IBaseRepository(ABC, Generic[TEntity]):
    """Interface trừu tượng cơ sở (Generic Base Repository) cho các thao tác CRUD chung.

    Cung cấp các phương thức truy vấn và lưu trữ cơ bản nhất (get_by_id, save, delete).
    """

    @abstractmethod
    async def get_by_id(self, entity_id: EntityID) -> TEntity | None:
        """Lấy thông tin thực thể theo ID."""
        pass

    @abstractmethod
    async def save(self, entity: TEntity) -> TEntity:
        """Lưu mới hoặc cập nhật thực thể."""
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể theo ID."""
        pass
