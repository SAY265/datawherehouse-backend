"""Input models độc lập HTTP cho phiên Agent."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class CreateSessionInput:
    project_id: EntityID
    title: str | None = None


@dataclass(frozen=True, slots=True)
class ListSessionsInput:
    project_id: EntityID


@dataclass(frozen=True, slots=True)
class GetSessionInput:
    session_id: EntityID


@dataclass(frozen=True, slots=True)
class RenameSessionInput:
    session_id: EntityID
    title: str


@dataclass(frozen=True, slots=True)
class ListSessionEventsInput:
    session_id: EntityID
    after_id: EntityID | None = None
    limit: int = 50


@dataclass(frozen=True, slots=True)
class SendSessionMessageInput:
    session_id: EntityID
    content: str
