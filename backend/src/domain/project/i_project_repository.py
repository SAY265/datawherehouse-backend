"""Giao diện repository cho Project."""

from abc import abstractmethod

from src.domain.project.entities import Project
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectRepository(IBaseRepository[Project]):
    """Định nghĩa các truy vấn persistence dành cho Project."""

    @abstractmethod
    async def list_accessible_by_user(self, user_id: EntityID) -> list[Project]:
        """Lấy các dự án người dùng được phép truy cập.

        Args:
            user_id: Định danh người dùng cần kiểm tra quyền.

        Returns:
            Danh sách dự án có thể truy cập.
        """
