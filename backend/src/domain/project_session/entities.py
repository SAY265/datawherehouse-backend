"""Thực thể thuộc miền Phiên Agent (Project Session Entities)."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.domain.project_session.enums import SessionEventRole, SessionEventType, SessionStatus
from src.domain.project_session.rules import validate_session_event
from src.domain.project_session.value_objects import SessionEventMetadata
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False)
class ProjectSession(BaseEntity):
    """Thực thể đại diện cho Phiên làm việc Dự án (Project Session)."""

    project_id: EntityID = field(default_factory=uuid4)
    user_id: EntityID = field(default_factory=uuid4)
    title: str = "Untitled Session"
    status: SessionStatus = SessionStatus.ACTIVE


@dataclass(eq=False)
class SessionEvent(BaseEntity):
    """Thực thể đại diện cho Sự kiện trong Phiên (Session Event)."""

    session_id: EntityID = field(default_factory=uuid4)
    role: SessionEventRole = SessionEventRole.USER
    type: SessionEventType = SessionEventType.MESSAGE
    content: str | None = None
    metadata: SessionEventMetadata | None = None

    def __post_init__(self) -> None:
        """Kiểm tra quy tắc nghiệp vụ cho SessionEvent và đảm bảo timezone UTC."""
        super().__post_init__()
        validate_session_event(self.session_id)
