"""Pydantic request DTO cho Sandbox API."""

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.application.sandbox.input import SandboxConnectionInput
from src.domain.sandbox.enums import SandboxDbType

SCHEMA_NAME_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"


class SandboxConnectionRequest(BaseModel):
    """Các trường kết nối dùng chung tại HTTP boundary."""

    model_config = ConfigDict(extra="forbid")
    db_type: SandboxDbType = Field(
        default=SandboxDbType.POSTGRESQL, description="Loại CSDL Sandbox"
    )
    host: str = Field(
        default="localhost", min_length=1, max_length=255, description="Host/IP kết nối"
    )
    port: int = Field(default=5432, ge=1, le=65535, description="Cổng kết nối DB")
    database_name: str = Field(
        default="sandbox_db", min_length=1, max_length=100, description="Tên CSDL"
    )
    username: str | None = Field(
        default=None, max_length=100, description="Tên đăng nhập"
    )
    password: str | None = Field(default=None, description="Mật khẩu kết nối")
    schema_name: str | None = Field(
        default="public",
        min_length=1,
        max_length=100,
        pattern=SCHEMA_NAME_PATTERN,
        description="Schema CSDL",
    )

    @model_validator(mode="after")
    def validate_supported_engine(self) -> "SandboxConnectionRequest":
        if self.db_type != SandboxDbType.POSTGRESQL:
            raise ValueError("Hiện tại chỉ hỗ trợ PostgreSQL Sandbox.")
        return self

    def to_application(self) -> SandboxConnectionInput:
        """Ánh xạ request sang application connection input."""
        return SandboxConnectionInput(
            self.db_type, self.host, self.port, self.database_name,
            self.username, self.password, self.schema_name,
        )


class SandboxConfigRequest(SandboxConnectionRequest):
    """Payload lưu cấu hình Sandbox."""


class TestConnectionRequest(SandboxConnectionRequest):
    """Payload kiểm tra kết nối Sandbox."""


class ExecuteDdlRequest(BaseModel):
    """Payload thực thi DDL trên Sandbox."""

    model_config = ConfigDict(extra="forbid")
    ddl_script: str = Field(
        min_length=1,
        max_length=1_000_000,
        description="Nội dung mã DDL script cần chạy",
    )
    reset_schema: bool = Field(
        default=True,
        description="Xoá và tạo lại schema đích trước khi chạy, trừ schema public.",
    )
