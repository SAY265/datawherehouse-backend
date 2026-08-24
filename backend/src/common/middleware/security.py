"""Middleware thiết lập các Security Headers chuẩn hóa cho ứng dụng HTTP (security.py)."""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware tự động đính kèm các Security Headers bảo vệ ứng dụng HTTP khỏi các lỗ hổng phổ biến (XSS, Clickjacking, MIME sniffing)."""

    def __init__(self, app: Callable, enable_hsts: bool = False) -> None:
        super().__init__(app)
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)

        # 1. Chống MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 2. Chống Clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # 3. Bảo vệ thông tin Referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 4. Kích hoạt XSS Protection bộ lọc trình duyệt
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. HSTS nếu được bật cho môi trường HTTPS Production
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
