"""Quản lý ngữ cảnh thực thi Interceptor (context.py).

Cung cấp InterceptorContext chứa thông tin operation_name, request_id, correlation_id,
session_id và metadata mở rộng mà không phụ thuộc vào HTTP request hay FastAPI.
"""

from dataclasses import dataclass, field
from typing import Any

from src.common.logging.context import (
    get_correlation_id,
    get_request_id,
    get_session_id,
)


@dataclass
class InterceptorContext:
    """Ngữ cảnh thực thi ứng dụng truyền qua chuỗi Interceptors.

    Ghi nhận metadata hoạt động độc lập với HTTP lifecycle.
    """

    operation_name: str
    request_id: str | None = field(default_factory=get_request_id)
    correlation_id: str | None = field(default_factory=get_correlation_id)
    session_id: str | None = field(default_factory=get_session_id)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        operation_name: str,
        *,
        request_id: str | None = None,
        correlation_id: str | None = None,
        session_id: str | None = None,
        **metadata: Any,
    ) -> "InterceptorContext":
        """Factory method hỗ trợ khởi tạo InterceptorContext linh hoạt."""
        return cls(
            operation_name=operation_name,
            request_id=request_id if request_id is not None else get_request_id(),
            correlation_id=correlation_id if correlation_id is not None else get_correlation_id(),
            session_id=session_id if session_id is not None else get_session_id(),
            metadata=metadata,
        )
