"""Entity cấu hình kết nối Sandbox."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.string import safe_strip
from src.domain.sandbox.enums import SandboxDbType, SandboxStatus
from src.domain.sandbox.rules import (
    normalize_sandbox_endpoint,
    normalize_schema_name,
    validate_sandbox_engine,
)
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID

DEFAULT_SANDBOX_HOST = "127.0.0.1"
DEFAULT_SANDBOX_PORT = 5432
DEFAULT_SANDBOX_DATABASE = "sandbox_db"
DEFAULT_SANDBOX_SCHEMA = "public"


@dataclass(eq=False, kw_only=True)
class SandboxConfig(BaseEntity):
    """Cấu hình persistence của cơ sở dữ liệu Sandbox."""

    project_id: EntityID
    db_type: SandboxDbType = SandboxDbType.POSTGRESQL
    host: str = DEFAULT_SANDBOX_HOST
    port: int = DEFAULT_SANDBOX_PORT
    database_name: str = DEFAULT_SANDBOX_DATABASE
    username: str | None = None
    password: str | None = None
    schema_name: str | None = DEFAULT_SANDBOX_SCHEMA
    status: SandboxStatus = SandboxStatus.CONFIGURED

    def __post_init__(self) -> None:
        """Bảo vệ invariant cấu hình và chuẩn hóa timestamp UTC.

        Raises:
            BusinessException: Khi engine hoặc endpoint không hợp lệ.
        """
        super().__post_init__()
        self.db_type = normalize_str_enum(
            self.db_type,
            SandboxDbType,
            ErrorCode.UNSUPPORTED_SANDBOX_DB_TYPE,
        )
        self.status = normalize_str_enum(
            self.status,
            SandboxStatus,
            ErrorCode.VALIDATION_ERROR,
        )
        validate_sandbox_engine(self.db_type)
        self.host, self.port, self.database_name = normalize_sandbox_endpoint(
            self.host,
            self.port,
            self.database_name,
        )
        self.username = safe_strip(self.username)
        self.schema_name = normalize_schema_name(self.schema_name)
