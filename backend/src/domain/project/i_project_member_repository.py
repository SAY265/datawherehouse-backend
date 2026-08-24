"""Giao diện repository cho ProjectMember."""

from abc import abstractmethod

from src.domain.project.entities import ProjectMember
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectMemberRepository(IBaseRepository[ProjectMember]):
    """Định nghĩa các truy vấn persistence dành cho thành viên dự án."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        """Lấy danh sách thành viên của dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Danh sách membership của dự án.
        """

    @abstractmethod
    async def get_by_project_and_user(
        self,
        project_id: EntityID,
        user_id: EntityID,
    ) -> ProjectMember | None:
        """Lấy membership duy nhất của người dùng trong dự án.

        Args:
            project_id: Định danh dự án.
            user_id: Định danh người dùng.

        Returns:
            Membership tương ứng hoặc ``None`` nếu không tồn tại.
        """
