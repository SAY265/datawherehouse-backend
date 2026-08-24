"""Interface cho Service Quản lý Cấu hình Sandbox (UC9.1)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.application.sandbox.dto import (
    SandboxConfigRequest,
    SandboxConfigResponse,
    TestConnectionRequest,
    TestConnectionResponse,
)


class ISandboxConfigService(ABC):
    """Interface định nghĩa hợp đồng quản lý cấu hình và kiểm tra kết nối Sandbox DB."""

    @abstractmethod
    async def get_config(self, project_id: UUID) -> SandboxConfigResponse | None:
        """Lấy cấu hình Sandbox DB của dự án."""
        pass

    @abstractmethod
    async def save_config(self, project_id: UUID, request: SandboxConfigRequest) -> SandboxConfigResponse:
        """Lưu hoặc cập nhật cấu hình Sandbox DB cho dự án."""
        pass

    @abstractmethod
    async def test_connection(
        self,
        project_id: UUID,
        request: TestConnectionRequest,
    ) -> TestConnectionResponse:
        """Thử kết nối đến CSDL Sandbox với thông số truyền vào."""
        pass
