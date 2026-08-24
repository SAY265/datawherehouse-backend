"""Giao diện Repository cho miền Yêu cầu Phân tích."""

from abc import abstractmethod

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID


class IAnalyticalRequirementRepository(IBaseRepository[AnalyticalRequirement]):
    """Interface trừu tượng cho thao tác lưu trữ thực thể AnalyticalRequirement."""

    @abstractmethod
    async def get_by_requirement_id(self, requirement_id: EntityID) -> list[AnalyticalRequirement]:
        """Lấy danh sách chi tiết phân tích theo ID yêu cầu gốc."""
        pass
