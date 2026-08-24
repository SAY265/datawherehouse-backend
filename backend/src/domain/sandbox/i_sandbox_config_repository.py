"""Giao diện repository cho SandboxConfig."""

from abc import abstractmethod

from src.domain.sandbox.entities import SandboxConfig
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class ISandboxConfigRepository(IBaseRepository[SandboxConfig]):
    """Định nghĩa persistence dành cho cấu hình sandbox."""

    @abstractmethod
    async def get_by_project_id(self, project_id: EntityID) -> SandboxConfig | None:
        """Lấy cấu hình sandbox theo dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Cấu hình sandbox hoặc ``None`` nếu chưa được lưu.
        """
