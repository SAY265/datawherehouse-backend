"""Thực thể và Value Objects cho miền Sandbox."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.common.utils.datetime import utc_now
from src.common.utils.uuid import generate_uuid
from src.domain.sandbox.enums import SandboxDbType


@dataclass
class StatementLog:
    """Value object lưu log thực thi của một câu lệnh SQL."""

    statement: str
    is_success: bool
    execution_time_ms: float
    timestamp: str
    error_detail: str | None = None


@dataclass
class SandboxConfig:
    """Thực thể Cấu hình Sandbox DB."""

    project_id: UUID
    db_type: SandboxDbType = SandboxDbType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database_name: str = "sandbox_db"
    username: str | None = None
    password: str | None = None
    schema_name: str | None = "public"
    id: UUID = field(default_factory=generate_uuid)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class SandboxExecutionResult:
    """Value object kết quả thực thi DDL trên Sandbox DB."""

    success: bool
    executed_statements: int
    succeeded_statements: int
    failed_statements: int
    total_duration_ms: float
    logs: list[StatementLog] = field(default_factory=list)
