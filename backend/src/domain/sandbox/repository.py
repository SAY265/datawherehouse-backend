"""Interface repository cho miền Sandbox."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.sandbox.sandbox import SandboxConfig


class ISandboxConfigRepository(ABC):
    """Interface định nghĩa truy xuất dữ liệu Cấu hình Sandbox."""

    @abstractmethod
    async def get_by_project_id(self, project_id: UUID) -> SandboxConfig | None:
        """Lấy cấu hình Sandbox theo ID dự án."""
        pass

    @abstractmethod
    async def save(self, config: SandboxConfig) -> SandboxConfig:
        """Lưu hoặc cập nhật cấu hình Sandbox."""
        pass
