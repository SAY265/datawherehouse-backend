"""Chuyển đổi lỗi SQLAlchemy tại infrastructure boundary."""

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException

Parameters = ParamSpec("Parameters")
Result = TypeVar("Result")


def translate_database_errors(
    operation: Callable[Parameters, Coroutine[Any, Any, Result]],
) -> Callable[Parameters, Coroutine[Any, Any, Result]]:
    """Bọc async database operation và giữ nguyên chữ ký coroutine.

    Args:
        operation: Coroutine thao tác với SQLAlchemy cần dịch lỗi.

    Returns:
        Coroutine cùng parameter/return contract với operation ban đầu.

    Raises:
        InfrastructureException: Khi SQLAlchemy phát sinh lỗi cơ sở dữ liệu.
    """

    @wraps(operation)
    async def translated(
        *args: Parameters.args,
        **kwargs: Parameters.kwargs,
    ) -> Result:
        try:
            return await operation(*args, **kwargs)
        except SQLAlchemyError as exc:
            raise InfrastructureException(
                code=ErrorCode.DATABASE_ERROR,
                message="Không thể hoàn tất thao tác cơ sở dữ liệu.",
            ) from exc

    return translated
