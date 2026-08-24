"""Ngoại lệ dành cho tầng Infrastructure (Infrastructure & External Service Errors)."""

from src.common.exceptions.system import SystemException


class InfrastructureException(SystemException):
    """Ngoại lệ dành cho tầng Infrastructure khi bắt lỗi kỹ thuật từ các thư viện/dịch vụ ngoài.

    Được ném ra từ tầng Infrastructure sau khi catch external exception (SQLAlchemyError,
    RedisError, OpenAIError, LangGraphError...) và translate bằng `raise ... from exc`.
    Kế thừa từ SystemException để đảm bảo tính thống nhất với Global Exception Handler.
    """

    pass
