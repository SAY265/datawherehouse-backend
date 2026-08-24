"""Public service contract và outbound ports của Sandbox module."""

from abc import ABC, abstractmethod

from src.application.sandbox.input import (
    ExecuteSandboxDdlInput,
    GetSandboxConfigInput,
    SandboxConnectionInput,
    SaveSandboxConfigInput,
    TestSandboxConnectionInput,
)
from src.application.sandbox.output import (
    ConnectionTestOutput,
    SandboxConfigOutput,
    SandboxExecutionOutput,
)
from src.domain.sandbox.entities import SandboxConfig


class ISandboxExecutor(ABC):
    """Outbound port thao tác với Sandbox database."""

    @abstractmethod
    async def test_connection(self, settings: SandboxConnectionInput) -> ConnectionTestOutput:
        """Kiểm tra kết nối mà không thay đổi database."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        config: SandboxConfig,
        ddl_script: str,
        reset_schema: bool,
    ) -> SandboxExecutionOutput:
        """Thực thi DDL bằng config đã vượt Domain validation."""
        raise NotImplementedError


class ISandboxService(ABC):
    """Hợp đồng quản lý config, codegen và thực thi Sandbox."""

    @abstractmethod
    async def get_config(self, data: GetSandboxConfigInput) -> SandboxConfigOutput | None:
        """Lấy cấu hình Sandbox của Project."""
        raise NotImplementedError

    @abstractmethod
    async def save_config(self, data: SaveSandboxConfigInput) -> SandboxConfigOutput:
        """Lưu cấu hình Sandbox của Project."""
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self, data: TestSandboxConnectionInput) -> ConnectionTestOutput:
        """Kiểm tra cấu hình kết nối mà không lưu."""
        raise NotImplementedError

    @abstractmethod
    async def execute_ddl(self, data: ExecuteSandboxDdlInput) -> SandboxExecutionOutput:
        """Thực thi script DDL bằng cấu hình đã lưu."""
        raise NotImplementedError
