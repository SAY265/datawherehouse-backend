"""Lớp ngoại lệ cơ sở (Base Exception) cho toàn bộ ứng dụng."""

from typing import Any

from src.common.exceptions.error_codes import ErrorCode


class AppException(Exception):  # noqa: N818
    """Lớp ngoại lệ cơ bản của hệ thống.

    Không phụ thuộc vào bất kỳ HTTP framework nào (FastAPI, Starlette).
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Any | None = None,
    ) -> None:
        """Khởi tạo AppException.

        Args:
            code: Mã lỗi dạng ErrorCode Enum.
            message: Thông điệp lỗi mô tả cho người dùng.
            details: Chi tiết lỗi bổ sung (nếu có).
        """
        super().__init__(message)
        self.code: ErrorCode = code
        self.message: str = message
        self.details: Any | None = details

    def __repr__(self) -> str:
        """Chuỗi đại diện cho đối tượng Exception."""
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r}, details={self.details!r})"

    def __str__(self) -> str:
        """Chuỗi hiển thị mô tả lỗi."""
        return f"[{self.code}] {self.message}"
