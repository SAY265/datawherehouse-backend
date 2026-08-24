"""Output models độc lập HTTP cho Sandbox application service."""

from dataclasses import dataclass

from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SandboxConfigOutput:
    id: EntityID
    project_id: EntityID
    db_type: SandboxDbType
    host: str
    port: int
    database_name: str
    username: str | None
    schema_name: str | None
    status: str = "CONFIGURED"

    @classmethod
    def from_domain(cls, config: SandboxConfig) -> "SandboxConfigOutput":
        """Ánh xạ config entity mà không làm lộ password."""
        return cls(
            id=config.id,
            project_id=config.project_id,
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            database_name=config.database_name,
            username=config.username,
            schema_name=config.schema_name,
            status=config.status.value if hasattr(config.status, "value") else str(config.status),
        )


@dataclass(frozen=True, slots=True)
class ConnectionTestOutput:
    success: bool
    message: str
    latency_ms: float | None = None


@dataclass(frozen=True, slots=True)
class StatementExecutionOutput:
    statement: str
    is_success: bool
    execution_time_ms: float
    timestamp: str
    error_detail: str | None = None


@dataclass(frozen=True, slots=True)
class SandboxExecutionOutput:
    success: bool
    executed_statements: int
    succeeded_statements: int
    failed_statements: int
    total_duration_ms: float
    logs: tuple[StatementExecutionOutput, ...] = ()
