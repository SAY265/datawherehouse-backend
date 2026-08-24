"""Giao diện Repository cho miền Dự án."""

from abc import abstractmethod

from src.domain.project.entities import Project, ProjectMember
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectRepository(IBaseRepository[Project]):
    """Interface trừu tượng cho thao tác lưu trữ và truy vấn thực thể Project."""

    @abstractmethod
    async def list_by_user(self, user_id: EntityID) -> list[Project]:
        """Lấy danh sách dự án sở hữu bởi người dùng."""
        pass


class IProjectMemberRepository(IBaseRepository[ProjectMember]):
    """Interface trừu tượng cho thao tác lưu trữ thqaành viên dự án."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        """Danh sách thành viên thuộc một dự án."""
        pass

    @abstractmethod
    async def is_member(self, project_id: EntityID, user_id: EntityID) -> bool:
        """Kiểm tra user có là thành viên dự án hay không."""
        pass
