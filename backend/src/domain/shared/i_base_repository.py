"""Giao diện repository cơ sở dùng chung cho tầng Domain."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID

TEntity = TypeVar("TEntity", bound=BaseEntity)


class IBaseRepository(ABC, Generic[TEntity]):
    """Định nghĩa các thao tác persistence tối thiểu cho entity."""

    @abstractmethod
    async def get_by_id(self, entity_id: EntityID) -> TEntity | None:
        """Lấy entity theo định danh.

        Args:
            entity_id: Định danh entity cần lấy.

        Returns:
            Entity tương ứng hoặc ``None`` khi không tồn tại.
        """

    @abstractmethod
    async def save(self, entity: TEntity) -> TEntity:
        """Lưu mới hoặc cập nhật entity.

        Args:
            entity: Entity cần lưu.

        Returns:
            Entity sau khi được persistence lưu.
        """

    @abstractmethod
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa entity theo định danh.

        Args:
            entity_id: Định danh entity cần xóa.

        Returns:
            ``True`` nếu entity đã được xóa, ngược lại ``False``.
        """
