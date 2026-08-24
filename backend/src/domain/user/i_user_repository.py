"""Giao diện repository cho User."""

from abc import abstractmethod

from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.user.entities import User


class IUserRepository(IBaseRepository[User]):
    """Định nghĩa các truy vấn persistence dành cho User."""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Lấy người dùng theo username.

        Args:
            username: Tên đăng nhập cần tra cứu.

        Returns:
            Người dùng tương ứng hoặc ``None`` nếu không tồn tại.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Lấy người dùng theo địa chỉ email.

        Args:
            email: Email đã chuẩn hóa cần tra cứu.

        Returns:
            Người dùng tương ứng hoặc ``None`` nếu không tồn tại.
        """
