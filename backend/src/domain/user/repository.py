"""Giao diện Repository cho thực thể Người dùng (User)."""

from abc import abstractmethod

from src.domain.shared.repository import IBaseRepository
from src.domain.user.entities import User


class IUserRepository(IBaseRepository[User]):
    """Interface trừu tượng cho thao tác lưu trữ và truy vấn thực thể User."""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Lấy thông tin người dùng theo tên đăng nhập."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Lấy thông tin người dùng theo địa chỉ email."""
        pass
