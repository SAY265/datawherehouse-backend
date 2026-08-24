"""Common Middleware Package.

Cung cấp các Middleware xử lý các cross-cutting concerns:
- Request ID / Correlation ID context management
- HTTP Request lifecycle logging & duration timing
- Security headers injection
- CORS policy configuration
"""

from src.common.middleware.cors import setup_cors_middleware
from src.common.middleware.logging import HTTPLoggingMiddleware
from src.common.middleware.request_id import RequestIDMiddleware
from src.common.middleware.security import SecurityHeadersMiddleware

__all__ = [
    "RequestIDMiddleware",
    "HTTPLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "setup_cors_middleware",
]
