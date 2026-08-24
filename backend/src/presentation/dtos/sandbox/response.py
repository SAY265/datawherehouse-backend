"""Pydantic response DTO cho Sandbox API."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.sandbox.output import (
    ConnectionTestOutput,
    SandboxConfigOutput,
    SandboxExecutionOutput,
)
from src.domain.sandbox.enums import SandboxDbType


class SandboxConfigResponse(BaseModel):
    """Cấu hình Sandbox không làm lộ mật khẩu."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    db_type: SandboxDbType
    host: str
    port: int
    database_name: str
    username: str | None = None
    schema_name: str | None = "public"
    status: str = "CONFIGURED"

    @classmethod
    def from_application(cls, output: SandboxConfigOutput) -> "SandboxConfigResponse":
        return cls.model_validate(output)


class TestConnectionResponse(BaseModel):
    """Kết quả kiểm tra kết nối Sandbox."""

    model_config = ConfigDict(from_attributes=True)
    success: bool
    message: str
    latency_ms: float | None = None

    @classmethod
    def from_application(cls, output: ConnectionTestOutput) -> "TestConnectionResponse":
        return cls.model_validate(output)


class StatementLogResponse(BaseModel):
    """Kết quả thực thi của một DDL statement."""

    model_config = ConfigDict(from_attributes=True)
    statement: str
    is_success: bool
    execution_time_ms: float
    timestamp: str
    error_detail: str | None = None


class ExecuteDdlResponse(BaseModel):
    """Kết quả thực thi toàn bộ DDL script."""

    model_config = ConfigDict(from_attributes=True)
    success: bool
    executed_statements: int
    succeeded_statements: int
    failed_statements: int
    total_duration_ms: float
    logs: list[StatementLogResponse] = Field(description="Log theo từng DDL statement")

    @classmethod
    def from_application(cls, output: SandboxExecutionOutput) -> "ExecuteDdlResponse":
        return cls.model_validate(output)
