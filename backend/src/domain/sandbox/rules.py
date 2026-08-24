"""Quy tắc nghiệp vụ cho cấu hình Sandbox."""

import re

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.sandbox.enums import SandboxDbType

MIN_PORT = 1
MAX_PORT = 65_535
MAX_HOST_LENGTH = 255
MAX_DATABASE_NAME_LENGTH = 100
MAX_SCHEMA_NAME_LENGTH = 100
SCHEMA_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_sandbox_engine(db_type: SandboxDbType) -> None:
    """Bảo đảm engine Sandbox được hệ thống hỗ trợ.

    Args:
        db_type: Loại cơ sở dữ liệu cần kiểm tra.

    Raises:
        BusinessException: Khi engine không phải PostgreSQL.
    """
    if db_type != SandboxDbType.POSTGRESQL:
        raise BusinessException(
            code=ErrorCode.UNSUPPORTED_SANDBOX_DB_TYPE,
            message="Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.",
        )


def normalize_sandbox_endpoint(
    host: str,
    port: int,
    database_name: str,
) -> tuple[str, int, str]:
    """Kiểm tra và chuẩn hóa endpoint kết nối Sandbox.

    Args:
        host: Host kết nối.
        port: Cổng TCP.
        database_name: Tên cơ sở dữ liệu.

    Returns:
        Host, port và database đã chuẩn hóa.

    Raises:
        BusinessException: Khi một thành phần endpoint không hợp lệ.
    """
    normalized_host = host.strip()
    normalized_database = database_name.strip()
    if not normalized_host or len(normalized_host) > MAX_HOST_LENGTH:
        _raise_invalid_config("Host Sandbox không hợp lệ.")
    if not isinstance(port, int) or isinstance(port, bool) or not MIN_PORT <= port <= MAX_PORT:
        _raise_invalid_config("Cổng Sandbox phải nằm trong khoảng 1 đến 65535.")
    if not normalized_database or len(normalized_database) > MAX_DATABASE_NAME_LENGTH:
        _raise_invalid_config("Tên cơ sở dữ liệu Sandbox không hợp lệ.")
    return normalized_host, port, normalized_database


def normalize_schema_name(schema_name: str | None) -> str | None:
    """Kiểm tra và chuẩn hóa tên schema tùy chọn.

    Args:
        schema_name: Tên schema hoặc ``None``.

    Returns:
        Tên schema đã trim hoặc ``None``.

    Raises:
        BusinessException: Khi schema không phải SQL identifier hợp lệ.
    """
    if schema_name is None:
        return None
    normalized = schema_name.strip()
    if len(normalized) > MAX_SCHEMA_NAME_LENGTH or not SCHEMA_NAME_PATTERN.fullmatch(normalized):
        _raise_invalid_config("Tên schema Sandbox không hợp lệ.")
    return normalized


def _raise_invalid_config(message: str) -> None:
    """Ném lỗi nghiệp vụ thống nhất cho cấu hình Sandbox."""
    raise BusinessException(code=ErrorCode.INVALID_SANDBOX_CONFIG, message=message)
