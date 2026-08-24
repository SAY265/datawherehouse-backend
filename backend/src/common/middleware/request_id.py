"""Middleware quản lý và xác thực Request ID / Correlation ID (request_id.py)."""

import re
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from src.common.logging.context import (
    clear_logging_context,
    set_correlation_id,
    set_request_id,
)
from starlette.middleware.base import BaseHTTPMiddleware

# Regex cho phép alphanumeric, gạch ngang, gạch dưới, độ dài 1-64
VALID_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")


def _is_valid_id(request_id: str | None) -> bool:
    """Kiểm tra request ID có hợp lệ và an toàn không (chống log injection)."""
    if not request_id:
        return False
    return bool(VALID_ID_PATTERN.match(request_id.strip()))


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware trích xuất hoặc khởi tạo Request ID & Correlation ID cho từng HTTP Request.

    Đảm bảo:
    - Validate input ID của client (ngăn chặn log injection, newline, control chars).
    - Tạo UUID4 mới nếu thiếu hoặc ID của client không hợp lệ.
    - Đồng bộ Request ID & Correlation ID vào ContextVar bất đồng bộ.
    - Đính kèm X-Request-ID và X-Correlation-ID vào HTTP Response Headers.
    - Tự động dọn dẹp ContextVar sau khi kết thúc vòng đời request.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Trích xuất X-Request-ID & X-Correlation-ID từ request headers
        raw_request_id = request.headers.get("X-Request-ID")
        raw_correlation_id = request.headers.get("X-Correlation-ID")

        # 2. Validation & Fallback generation
        if _is_valid_id(raw_request_id):
            request_id = raw_request_id.strip()
        else:
            request_id = str(uuid.uuid4())

        correlation_id = raw_correlation_id.strip() if _is_valid_id(raw_correlation_id) else None

        # 3. Ghi nhận contextvars
        set_request_id(request_id)
        if correlation_id:
            set_correlation_id(correlation_id)

        try:
            response: Response = await call_next(request)

            # 4. Gắn X-Request-ID và X-Correlation-ID vào response headers
            response.headers["X-Request-ID"] = request_id
            if correlation_id:
                response.headers["X-Correlation-ID"] = correlation_id

            return response
        finally:
            # 5. Dọn dẹp context sau khi kết thúc request
            clear_logging_context()
