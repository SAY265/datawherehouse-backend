"""Cấu hình và đăng ký CORS Middleware chuẩn hóa (cors.py)."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors_middleware(app: FastAPI, settings: Any) -> None:
    """Cấu hình và gắn CORSMiddleware vào ứng dụng FastAPI dựa trên Settings.

    Đảm bảo:
    - Origins được trích xuất từ settings.cors_origins_list.
    - Configured methods & headers linh hoạt theo môi trường.
    - Tuân thủ quy định an toàn của CORS specification.
    """
    origins = settings.cors_origins_list
    allow_credentials = getattr(settings, "cors_allow_credentials", True)
    allow_methods = settings.cors_allow_methods_list
    allow_headers = settings.cors_allow_headers_list

    # Kiểm tra an toàn: Starlette không cho phép allow_origins=["*"] kết hợp allow_credentials=True
    if "*" in origins and allow_credentials:
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.trycloudflare\.com|https://.*\.loca\.lt",
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )
