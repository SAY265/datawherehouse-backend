"""Adapter kết nối PostgreSQL cho Sandbox."""

import time
from dataclasses import dataclass

import asyncpg
from src.application.sandbox.input import SandboxConnectionInput
from src.common.logging import get_logger
from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType

logger = get_logger(__name__)
CONNECTION_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True, slots=True)
class PostgresConnectionParameters:
    """Nhóm tham số namespace và xác thực kết nối."""

    host: str
    port: int
    database: str
    username: str
    password: str

    @classmethod
    def from_input(cls, data: SandboxConnectionInput) -> "PostgresConnectionParameters":
        """Tạo tham số từ input kiểm tra kết nối."""
        host = (data.host or "127.0.0.1").strip()
        if host.casefold() == "localhost":
            host = "127.0.0.1"
        return cls(
            host,
            data.port or 5432,
            data.database_name or "postgres",
            data.username or "postgres",
            data.password or "",
        )

    @classmethod
    def from_config(cls, config: SandboxConfig) -> "PostgresConnectionParameters":
        """Tạo tham số từ Domain config đã giải mã."""
        host = (config.host or "127.0.0.1").strip()
        if host.casefold() == "localhost":
            host = "127.0.0.1"
        return cls(
            host,
            config.port,
            config.database_name,
            config.username or "postgres",
            config.password or "",
        )


async def connect(parameters: PostgresConnectionParameters) -> asyncpg.Connection:
    """Mở kết nối PostgreSQL với timeout có tên."""
    return await asyncpg.connect(
        host=parameters.host,
        port=parameters.port,
        database=parameters.database,
        user=parameters.username,
        password=parameters.password,
        timeout=CONNECTION_TIMEOUT_SECONDS,
    )


async def check_connection(data: SandboxConnectionInput) -> tuple[bool, str, float]:
    """Kiểm tra kết nối và không làm lộ chi tiết driver."""
    started_at = time.perf_counter()
    if data.db_type != SandboxDbType.POSTGRESQL:
        return _connection_result(False, "Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.", started_at)
    connection: asyncpg.Connection | None = None
    try:
        connection = await connect(PostgresConnectionParameters.from_input(data))
        return _connection_result(True, "Kết nối thành công đến PostgreSQL Sandbox!", started_at)
    except (OSError, asyncpg.PostgresError) as exc:
        logger.warning("sandbox_connection_failed error_type=%s", type(exc).__name__)
        return _connection_result(False, "Không thể kết nối đến Sandbox Database.", started_at)
    finally:
        if connection is not None:
            await connection.close()


def _connection_result(success: bool, message: str, started_at: float) -> tuple[bool, str, float]:
    """Tạo kết quả kiểm tra kết nối có latency."""
    latency = round((time.perf_counter() - started_at) * 1000, 2)
    return success, message, latency
