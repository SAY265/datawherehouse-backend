"""Giao diện Repository cho miền Phiên Agent (Agent Session)."""

from abc import abstractmethod

from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectSessionRepository(IBaseRepository[ProjectSession]):
    """Interface trừu tượng cho thao tác lưu trữ và truy vấn thực thể ProjectSession."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[ProjectSession]:
        """Danh sách các phiên thuộc một dự án."""
        pass


class ISessionEventRepository(IBaseRepository[SessionEvent]):
    """Interface trừu tượng cho thao tác lưu trữ sự kiện trong phiên (SessionEvent)."""

    @abstractmethod
    async def list_by_session(self, session_id: EntityID) -> list[SessionEvent]:
        """Danh sách các sự kiện thuộc một phiên làm việc."""
        pass
