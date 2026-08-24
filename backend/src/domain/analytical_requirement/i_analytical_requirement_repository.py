"""Giao diện repository cho AnalyticalRequirement."""

from abc import abstractmethod

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IAnalyticalRequirementRepository(IBaseRepository[AnalyticalRequirement]):
    """Định nghĩa persistence dành cho yêu cầu phân tích."""

    @abstractmethod
    async def get_by_requirement_id(
        self,
        requirement_id: EntityID,
    ) -> list[AnalyticalRequirement]:
        """Lấy các yêu cầu phân tích theo yêu cầu gốc.

        Args:
            requirement_id: Định danh yêu cầu nghiệp vụ gốc.

        Returns:
            Danh sách yêu cầu phân tích liên quan.
        """

    @abstractmethod
    async def list_by_project(
        self, project_id: EntityID
    ) -> list[AnalyticalRequirement]:
        """Lấy toàn bộ yêu cầu phân tích thuộc dự án."""

    @abstractmethod
    async def replace_by_project(
        self,
        project_id: EntityID,
        entities: tuple[AnalyticalRequirement, ...],
    ) -> list[AnalyticalRequirement]:
        """Thay atomically toàn bộ AnalyticalRequirements của dự án."""
