"""Cấu hình tập trung cho toàn bộ hệ thống Logging (config.py)."""

import logging
import sys
from typing import Any

from src.common.logging.filters import ContextLogFilter, SensitiveDataFilter
from src.common.logging.formatters import ConsoleFormatter, JsonFormatter


def configure_logging(settings: Any) -> None:
    """Khởi tạo và thiết lập cấu hình Logging toàn hệ thống dựa vào Settings."""
    log_level_str: str = getattr(settings, "log_level", "INFO").upper()
    log_level: int = getattr(logging, log_level_str, logging.INFO)
    app_env: str = getattr(settings, "app_env", "development")
    log_format_setting: str = getattr(settings, "log_format", "console")

    # Chọn Formatter dựa vào app_env hoặc log_format setting
    if app_env == "production" or log_format_setting.lower() == "json":
        formatter: logging.Formatter = JsonFormatter()
    else:
        formatter = ConsoleFormatter()

    # Ensure UTF-8 output on Windows streams
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass

    # Cấu hình Handler ghi ra stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    handler.addFilter(ContextLogFilter())
    handler.addFilter(SensitiveDataFilter())

    # Khởi tạo Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Xóa các handler mặc định cũ để tránh duplicate log
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    root_logger.addHandler(handler)

    # Điều chỉnh log level của các 3rd-party loggers để tránh rác log
    third_party_loggers = ["sqlalchemy", "httpx", "httpcore", "urllib3"]
    for logger_name in third_party_loggers:
        tp_logger = logging.getLogger(logger_name)
        tp_logger.setLevel(max(log_level, logging.WARNING))
        tp_logger.propagate = True

    # Cấu hình Uvicorn logger nhất quán
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers = []
    uvicorn_error_logger.propagate = True

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = []
    uvicorn_access_logger.propagate = True
