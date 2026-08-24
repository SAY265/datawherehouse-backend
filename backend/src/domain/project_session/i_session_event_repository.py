"""Giao diện repository cho SessionEvent."""

from abc import abstractmethod

from src.domain.project_session.entities import SessionEvent
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class ISessionEventRepository(IBaseRepository[SessionEvent]):
    """Định nghĩa persistence dành cho sự kiện phiên làm việc."""

    @abstractmethod
    async def list_by_session(
        self,
        session_id: EntityID,
        after_id: EntityID | None = None,
        limit: int = 50,
    ) -> list[SessionEvent]:
        """Lấy danh sách sự kiện của một phiên làm việc.

        Args:
            session_id: Định danh phiên làm việc.

        Returns:
            Danh sách sự kiện của phiên.
        """
