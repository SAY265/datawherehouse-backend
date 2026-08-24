"""Điều phối validation, kết nối và transaction Sandbox."""

import re
import time

import asyncpg
from src.application.sandbox.output import SandboxExecutionOutput
from src.common.logging import get_logger
from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType
from src.infrastructure.sandbox.execution_results import failed_result
from src.infrastructure.sandbox.postgres_connection import PostgresConnectionParameters, connect
from src.infrastructure.sandbox.postgres_ddl_validator import split_ddl_statements
from src.infrastructure.sandbox.postgres_transaction_executor import (
    TransactionExecution,
    execute_transaction,
)

logger = get_logger(__name__)
SCHEMA_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DEFAULT_SCHEMA = "public"


async def execute_sandbox_ddl(
    config: SandboxConfig,
    ddl_script: str,
    reset_schema: bool = True,
) -> SandboxExecutionOutput:
    """Xác thực và thực thi toàn bộ DDL trong một transaction."""
    started_at = time.perf_counter()
    validation = _validate_input(config, ddl_script, started_at)
    if isinstance(validation, SandboxExecutionOutput):
        return validation
    schema_name, statements = validation
    try:
        connection = await connect(PostgresConnectionParameters.from_config(config))
    except (OSError, asyncpg.PostgresError) as exc:
        logger.warning("sandbox_connection_failed error_type=%s", type(exc).__name__)
        return failed_result("[connection]", "Không thể kết nối đến Sandbox Database.", started_at)
    try:
        execution = TransactionExecution(schema_name, statements, reset_schema, started_at)
        return await execute_transaction(connection, execution)
    finally:
        await connection.close()


def _validate_input(
    config: SandboxConfig,
    ddl_script: str,
    started_at: float,
) -> tuple[str, list[str]] | SandboxExecutionOutput:
    """Kiểm tra engine, schema và script trước khi kết nối."""
    if config.db_type != SandboxDbType.POSTGRESQL:
        return failed_result("[engine]", "Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.", started_at)
    schema_name = config.schema_name or DEFAULT_SCHEMA
    if not SCHEMA_PATTERN.fullmatch(schema_name):
        return failed_result("[schema]", "Tên schema không hợp lệ.", started_at)
    try:
        statements = split_ddl_statements(ddl_script, schema_name)
    except ValueError as exc:
        return failed_result("[validation]", str(exc), started_at)
    if not statements:
        return failed_result("[validation]", "DDL script không có câu lệnh.", started_at)
    return schema_name, statements
