"""Giao diện Repository cho miền Yêu cầu (Requirement)."""

from abc import abstractmethod

from src.domain.requirement.entities import Requirement
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID


class IRequirementRepository(IBaseRepository[Requirement]):
    """Interface trừu tượng cho thao tác lưu trữ và truy vấn thực thể Requirement."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        """Lấy danh sách yêu cầu thuộc một dự án."""
        pass
