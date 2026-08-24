"""Middleware ghi log cho vòng đời HTTP Request (logging.py)."""

import time
from collections.abc import Callable

from fastapi import Request, Response
from src.common.logging.logger import get_logger
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)

# Các đường dẫn endpoint kiểm tra sức khỏe hệ thống cần lọc bớt log INFO
QUIET_PATHS = {"/health", "/healthz", "/ready", "/readyz"}


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware theo dõi vòng đời HTTP Request, đo đạc thời gian thực thi (duration_ms) và ghi log.

    Đặc điểm:
    - Sử dụng monotonic clock (time.perf_counter()) để đo chính xác duration.
    - Phân loại log level: DEBUG cho health check & OPTIONS preflight, INFO cho request thông thường.
    - Đảm bảo an toàn với StreamingResponse (không buffer/consume body).
    - Không nuốt Exception: Re-raise exception để Global Exception Handler xử lý.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        path = request.url.path
        method = request.method

        # Xác định log level phù hợp (health check & OPTIONS -> DEBUG)
        is_quiet = path in QUIET_PATHS or method == "OPTIONS"
        log_func = logger.debug if is_quiet else logger.info

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            log_func(
                "http_request_completed: %s %s status=%d duration_ms=%.2f",
                method,
                path,
                response.status_code,
                duration_ms,
            )

            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning(
                "http_request_failed: %s %s duration_ms=%.2f error=%s",
                method,
                path,
                duration_ms,
                str(exc),
            )
            raise
