"""Giao diện repository cho ProjectSession."""

from abc import abstractmethod

from src.domain.project_session.entities import ProjectSession
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectSessionRepository(IBaseRepository[ProjectSession]):
    @abstractmethod
    async def get_by_id_for_update(
        self, entity_id: EntityID
    ) -> ProjectSession | None:
        """Load a session with a row lock for turn acquisition."""

    """Định nghĩa persistence dành cho phiên làm việc dự án."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[ProjectSession]:
        """Lấy danh sách phiên làm việc của dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Danh sách phiên làm việc của dự án.
        """

    @abstractmethod
    async def list_by_project_user(
        self, project_id: EntityID, user_id: EntityID
    ) -> list[ProjectSession]:
        """Lấy các session của một người dùng trong project."""
