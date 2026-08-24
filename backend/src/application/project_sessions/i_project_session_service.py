"""Public service contract cho phiên Agent."""

from abc import ABC, abstractmethod

from src.application.project_sessions.input import (
    CreateSessionInput,
    GetSessionInput,
    ListSessionEventsInput,
    ListSessionsInput,
    RenameSessionInput,
    SendSessionMessageInput,
)
from src.application.project_sessions.output import ProjectSessionOutput, SessionEventOutput, SessionTurnOutput


class IProjectSessionService(ABC):
    """Điều phối lifecycle, lịch sử và lượt chạy Agent."""

    @abstractmethod
    async def create_session(self, data: CreateSessionInput) -> ProjectSessionOutput: ...

    @abstractmethod
    async def list_sessions(self, data: ListSessionsInput) -> tuple[ProjectSessionOutput, ...]: ...

    @abstractmethod
    async def get_session(self, data: GetSessionInput) -> ProjectSessionOutput: ...

    @abstractmethod
    async def rename_session(self, data: RenameSessionInput) -> ProjectSessionOutput: ...

    @abstractmethod
    async def list_events(self, data: ListSessionEventsInput) -> tuple[SessionEventOutput, ...]: ...

    @abstractmethod
    async def send_message(self, data: SendSessionMessageInput) -> SessionTurnOutput: ...
