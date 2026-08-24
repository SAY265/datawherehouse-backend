"""Giao diện repository cho Requirement."""

from abc import abstractmethod

from src.domain.requirement.entities import Requirement
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IRequirementRepository(IBaseRepository[Requirement]):
    """Định nghĩa các truy vấn persistence dành cho Requirement."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        """Lấy danh sách yêu cầu của dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Danh sách yêu cầu nghiệp vụ của dự án.
        """

    @abstractmethod
    async def replace_by_project(
        self, project_id: EntityID, entities: tuple[Requirement, ...]
    ) -> list[Requirement]:
        """Thay atomically toàn bộ Requirements của dự án."""
