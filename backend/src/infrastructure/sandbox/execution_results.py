"""Factory bất biến cho log và kết quả thực thi Sandbox."""

import time
from dataclasses import replace

from src.application.sandbox.output import SandboxExecutionOutput, StatementExecutionOutput
from src.common.utils.datetime import to_isoformat, utc_now


def error_log(statement: str, detail: str) -> StatementExecutionOutput:
    """Tạo một log thất bại đã được làm sạch."""
    return StatementExecutionOutput(statement, False, 0, to_isoformat(utc_now()), detail)


def failed_result(statement: str, detail: str, started_at: float) -> SandboxExecutionOutput:
    """Tạo kết quả thất bại trước khi chạy statement."""
    return SandboxExecutionOutput(
        success=False,
        executed_statements=0,
        succeeded_statements=0,
        failed_statements=0,
        total_duration_ms=_duration(started_at),
        logs=(error_log(statement, detail),),
    )


def result_from_logs(
    logs: list[StatementExecutionOutput],
    started_at: float,
    success: bool,
) -> SandboxExecutionOutput:
    """Tổng hợp log thành kết quả Application."""
    succeeded = sum(item.is_success for item in logs)
    return SandboxExecutionOutput(
        success=success,
        executed_statements=len(logs),
        succeeded_statements=succeeded,
        failed_statements=len(logs) - succeeded,
        total_duration_ms=_duration(started_at),
        logs=tuple(logs),
    )


def mark_rolled_back(
    logs: list[StatementExecutionOutput],
) -> list[StatementExecutionOutput]:
    """Đánh dấu các statement thành công đã bị rollback."""
    return [
        replace(
            item,
            is_success=False,
            error_detail="Đã rollback vì một câu lệnh khác thất bại.",
        )
        for item in logs
    ]


def _duration(started_at: float) -> float:
    """Tính thời lượng mili-giây."""
    return round((time.perf_counter() - started_at) * 1000, 2)
