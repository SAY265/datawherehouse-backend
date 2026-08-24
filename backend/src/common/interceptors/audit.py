"""Interceptor ghi nhận thông tin Audit Metadata (audit.py).

Ghi nhận thông tin audit mở rộng (actor, action, resource_id) cho operation
mà không lưu trữ dữ liệu nhạy cảm hay can thiệp vào CSDL.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from src.common.interceptors.base import BaseInterceptor
from src.common.interceptors.context import InterceptorContext
from src.common.utils.datetime import utc_now


class AuditInterceptor(BaseInterceptor):
    """Interceptor đính kèm và kiểm tra Audit Metadata."""

    def __init__(
        self,
        actor: str | None = None,
        action: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        self.actor = actor
        self.action = action
        self.resource_id = resource_id

    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[Any]],
    ) -> Any:
        audit_record: dict[str, Any] = {
            "timestamp": utc_now().isoformat(),
            "actor": self.actor or context.metadata.get("actor", "system"),
            "action": self.action or context.operation_name,
            "resource_id": self.resource_id or context.metadata.get("resource_id"),
        }
        # Đính kèm audit record vào context metadata (loại bỏ các giá trị None)
        context.metadata["audit"] = {k: v for k, v in audit_record.items() if v is not None}

        return await call_next()
