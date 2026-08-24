"""Interceptor ghi log ở mức Application Operation (logging.py).

Ghi nhận các sự kiện application_operation_started, completed, failed
mà không duplicate log với HTTP Middleware hay Global Exception Handler.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from src.common.exceptions.base import AppException
from src.common.interceptors.base import BaseInterceptor
from src.common.interceptors.context import InterceptorContext
from src.common.logging import get_logger

logger = get_logger(__name__)


class LoggingInterceptor(BaseInterceptor):
    """Interceptor ghi log cho các thao tác tầng Application."""

    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[Any]],
    ) -> Any:
        # 1. Ghi log trước khi thực thi (Started)
        start_extra: dict[str, Any] = {
            "event": "application_operation_started",
            "operation": context.operation_name,
            "request_id": context.request_id,
            "session_id": context.session_id,
        }
        logger.info(
            f"Bắt đầu thực thi operation '{context.operation_name}'",
            extra={k: v for k, v in start_extra.items() if v is not None},
        )

        try:
            # 2. Thực thi operation tiếp theo trong chuỗi
            result = await call_next()

            # 3. Ghi log sau khi thực thi thành công (Completed)
            duration_ms = context.metadata.get("duration_ms")
            complete_extra: dict[str, Any] = {
                "event": "application_operation_completed",
                "operation": context.operation_name,
                "duration_ms": duration_ms,
                "request_id": context.request_id,
            }
            duration_str = f" trong {duration_ms:.2f}ms" if duration_ms is not None else ""
            logger.info(
                f"Hoàn tất operation '{context.operation_name}'{duration_str}",
                extra={k: v for k, v in complete_extra.items() if v is not None},
            )
            return result

        except Exception as exc:
            # 4. Ghi log khi xảy ra lỗi (Failed) và re-raise
            error_code = str(exc.code) if isinstance(exc, AppException) else None
            fail_extra: dict[str, Any] = {
                "event": "application_operation_failed",
                "operation": context.operation_name,
                "error_code": error_code,
                "request_id": context.request_id,
            }
            log_msg = f"Thất bại operation '{context.operation_name}': {exc}"

            # Phân loại mức log: Warning cho AppException nghiệp vụ, Error cho lỗi khác
            if isinstance(exc, AppException):
                logger.warning(
                    log_msg,
                    extra={k: v for k, v in fail_extra.items() if v is not None},
                )
            else:
                logger.error(
                    log_msg,
                    extra={k: v for k, v in fail_extra.items() if v is not None},
                )

            raise exc
