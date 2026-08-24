"""Input models độc lập HTTP cho Sandbox application service."""

from dataclasses import dataclass

from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SandboxConnectionInput:
    db_type: SandboxDbType
    host: str
    port: int
    database_name: str
    username: str | None = None
    password: str | None = None
    schema_name: str | None = None


@dataclass(frozen=True, slots=True)
class GetSandboxConfigInput:
    project_id: EntityID


@dataclass(frozen=True, slots=True)
class SaveSandboxConfigInput:
    project_id: EntityID
    connection: SandboxConnectionInput


@dataclass(frozen=True, slots=True)
class TestSandboxConnectionInput:
    project_id: EntityID
    connection: SandboxConnectionInput


@dataclass(frozen=True, slots=True)
class ExecuteSandboxDdlInput:
    project_id: EntityID
    ddl_script: str
    reset_schema: bool = True
