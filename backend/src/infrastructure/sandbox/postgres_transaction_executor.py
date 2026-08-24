"""Thực thi các statement PostgreSQL trong một transaction."""

import time
from dataclasses import dataclass

import asyncpg
from src.application.sandbox.output import SandboxExecutionOutput, StatementExecutionOutput
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.common.utils.datetime import to_isoformat, utc_now
from src.infrastructure.sandbox.execution_results import (
    error_log,
    mark_rolled_back,
    result_from_logs,
)

logger = get_logger(__name__)
PROTECTED_SCHEMA = "public"
LOCK_TIMEOUT = "5s"
STATEMENT_TIMEOUT = "30s"


@dataclass(frozen=True, slots=True)
class TransactionExecution:
    """Nhóm namespace, statement và timing của một lượt chạy."""

    schema_name: str
    statements: list[str]
    reset_schema: bool
    started_at: float


@dataclass(slots=True)
class TransactionContext:
    """Trạng thái kỹ thuật của transaction đang chạy."""

    connection: asyncpg.Connection
    execution: TransactionExecution
    transaction: object
    logs: list[StatementExecutionOutput]


async def execute_transaction(
    connection: asyncpg.Connection,
    execution: TransactionExecution,
) -> SandboxExecutionOutput:
    """Thiết lập transaction và dịch lỗi theo đúng boundary."""
    context = TransactionContext(connection, execution, connection.transaction(), [])
    try:
        return await _run_and_commit(context)
    except (OSError, TimeoutError, asyncpg.PostgresError) as exc:
        return await _driver_failure(context, exc)
    except Exception as exc:
        await _rollback_safely(context.transaction)
        raise InfrastructureException(
            code=ErrorCode.SANDBOX_EXECUTION_ERROR,
            message="Không thể hoàn tất transaction Sandbox.",
        ) from exc


async def _run_and_commit(context: TransactionContext) -> SandboxExecutionOutput:
    """Chạy các statement rồi commit hoặc rollback khi một statement lỗi."""
    await context.transaction.start()
    execution = context.execution
    await _prepare_namespace(context.connection, execution.schema_name, execution.reset_schema)
    for statement in execution.statements:
        log = await _run_statement(context.connection, statement)
        context.logs.append(log)
        if not log.is_success:
            await context.transaction.rollback()
            return _statement_failure(context.logs, execution.started_at)
    await context.transaction.commit()
    return result_from_logs(context.logs, execution.started_at, True)


async def _driver_failure(
    context: TransactionContext,
    error: Exception,
) -> SandboxExecutionOutput:
    """Dịch lỗi driver dự kiến thành execution result an toàn."""
    await _rollback_safely(context.transaction)
    logger.warning("sandbox_transaction_failed error_type=%s", type(error).__name__)
    logs = mark_rolled_back(context.logs)
    logs.append(error_log("[transaction]", "Transaction Sandbox thất bại."))
    return result_from_logs(logs, context.execution.started_at, False)


async def _prepare_namespace(
    connection: asyncpg.Connection,
    schema_name: str,
    reset_schema: bool,
) -> None:
    """Chuẩn bị schema và timeout bên trong transaction."""
    if reset_schema and schema_name != PROTECTED_SCHEMA:
        await connection.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
    await connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    await connection.execute(f'SET LOCAL search_path TO "{schema_name}"')
    await connection.execute(f"SET LOCAL lock_timeout TO '{LOCK_TIMEOUT}'")
    await connection.execute(f"SET LOCAL statement_timeout TO '{STATEMENT_TIMEOUT}'")


def _statement_failure(
    logs: list[StatementExecutionOutput],
    started_at: float,
) -> SandboxExecutionOutput:
    """Tạo kết quả rollback khi một statement thất bại."""
    return result_from_logs(mark_rolled_back(logs[:-1]) + [logs[-1]], started_at, False)


async def _run_statement(
    connection: asyncpg.Connection,
    statement: str,
) -> StatementExecutionOutput:
    """Chạy một statement và chuyển lỗi driver thành log an toàn."""
    started_at = time.perf_counter()
    try:
        await connection.execute(statement)
        return StatementExecutionOutput(
            statement, True, _duration(started_at), to_isoformat(utc_now())
        )
    except (OSError, TimeoutError, asyncpg.PostgresError) as exc:
        logger.warning("sandbox_statement_failed error_type=%s", type(exc).__name__)
        return StatementExecutionOutput(
            statement,
            False,
            _duration(started_at),
            to_isoformat(utc_now()),
            "Câu lệnh DDL thất bại.",
        )


async def _rollback_safely(transaction: object) -> None:
    """Rollback và chỉ ghi log nếu chính rollback thất bại."""
    try:
        await transaction.rollback()
    except Exception:
        logger.exception("sandbox_rollback_failed")


def _duration(started_at: float) -> float:
    """Tính thời lượng mili-giây."""
    return round((time.perf_counter() - started_at) * 1000, 2)
