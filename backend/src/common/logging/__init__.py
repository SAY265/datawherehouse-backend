"""Common Logging Module.

Cung cấp hệ thống logging tập trung, có cấu trúc (Structured Logging), tự động quản lý request context và bảo mật thông tin nhạy cảm.
"""

from src.common.logging.config import configure_logging
from src.common.logging.context import (
    clear_logging_context,
    get_agent_name,
    get_correlation_id,
    get_request_id,
    get_session_id,
    set_agent_name,
    set_correlation_id,
    set_request_id,
    set_session_id,
)
from src.common.logging.logger import get_logger

__all__ = [
    "get_logger",
    "configure_logging",
    "get_request_id",
    "set_request_id",
    "get_correlation_id",
    "set_correlation_id",
    "get_session_id",
    "set_session_id",
    "get_agent_name",
    "set_agent_name",
    "clear_logging_context",
]
