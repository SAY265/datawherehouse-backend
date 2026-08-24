"""Pydantic v2 DTOs cho miền Sandbox."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.domain.sandbox.enums import SandboxDbType

SCHEMA_NAME_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"


class SandboxConfigRequest(BaseModel):
    """DTO Yêu cầu cấu hình kết nối DB Sandbox."""

    model_config = ConfigDict(from_attributes=True)

    db_type: SandboxDbType = Field(default=SandboxDbType.POSTGRESQL, description="Loại CSDL Sandbox")
    host: str = Field(default="localhost", min_length=1, max_length=255, description="Host/IP kết nối")
    port: int = Field(default=5432, ge=1, le=65535, description="Cổng kết nối DB")
    database_name: str = Field(default="sandbox_db", min_length=1, max_length=100, description="Tên CSDL")
    username: str | None = Field(default=None, max_length=100, description="Tên đăng nhập")
    password: str | None = Field(default=None, description="Mật khẩu kết nối")
    schema_name: str | None = Field(
        default="public",
        min_length=1,
        max_length=100,
        pattern=SCHEMA_NAME_PATTERN,
        description="Schema CSDL",
    )

    @model_validator(mode="after")
    def validate_supported_engine(self) -> "SandboxConfigRequest":
        if self.db_type != SandboxDbType.POSTGRESQL:
            raise ValueError("Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.")
        return self


class SandboxConfigResponse(BaseModel):
    """DTO Trả về thông tin cấu hình Sandbox DB."""

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


class TestConnectionRequest(BaseModel):
    """DTO Yêu cầu kiểm tra kết nối Sandbox DB."""

    db_type: SandboxDbType = SandboxDbType.POSTGRESQL
    model_config = ConfigDict(extra="forbid")

    host: str = Field(default="localhost", min_length=1, max_length=255)
    port: int = Field(default=5432, ge=1, le=65535)
    database_name: str = Field(default="sandbox_db", min_length=1, max_length=100)
    username: str | None = Field(default=None, max_length=100)
    password: str | None = None
    schema_name: str | None = Field(
        default="public",
        min_length=1,
        max_length=100,
        pattern=SCHEMA_NAME_PATTERN,
    )

    @model_validator(mode="after")
    def validate_supported_engine(self) -> "TestConnectionRequest":
        if self.db_type != SandboxDbType.POSTGRESQL:
            raise ValueError("Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.")
        return self


class TestConnectionResponse(BaseModel):
    """DTO Trả về kết quả kiểm tra kết nối Sandbox DB."""

    success: bool
    message: str
    latency_ms: float | None = None


class ExecuteDdlRequest(BaseModel):
    """DTO Yêu cầu thực thi DDL script lên Sandbox DB."""

    ddl_script: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,
        description="Nội dung mã DDL script cần chạy",
    )


class StatementLogDto(BaseModel):
    """DTO Log dòng thực thi câu lệnh SQL."""

    statement: str
    is_success: bool
    execution_time_ms: float
    timestamp: str
    error_detail: str | None = None


class ExecuteDdlResponse(BaseModel):
    """DTO Trả về kết quả thực thi DDL script."""

    success: bool
    executed_statements: int
    succeeded_statements: int
    failed_statements: int
    total_duration_ms: float
    logs: list[StatementLogDto]


class FixDdlWithAiRequest(BaseModel):
    """DTO Yêu cầu AI sửa lỗi mã DDL."""

    ddl_script: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,
        description="Nội dung mã DDL đang gặp lỗi cần sửa",
    )
    error_message: str | None = Field(
        default=None,
        description="Thông điệp hoặc log lỗi khi chạy thử DDL trên Sandbox DB",
    )
    target_dialect: str = Field(
        default="postgresql",
        description="Loại CSDL đích (PostgreSQL, Snowflake, ClickHouse, BigQuery)",
    )
    logs: list[str] | None = Field(
        default=None,
        description="Danh sách các dòng log terminal chi tiết",
    )


class FixDdlWithAiResponse(BaseModel):
    """DTO Trả về kết quả DDL đã được sửa bởi AI."""

    fixed_ddl: str = Field(..., description="Mã DDL đã được sửa hoàn chỉnh")
    explanation: str = Field(..., description="Giải thích nguyên nhân và cách khắc phục")
    changes_made: list[str] = Field(default_factory=list, description="Danh sách các thay đổi chi tiết")

