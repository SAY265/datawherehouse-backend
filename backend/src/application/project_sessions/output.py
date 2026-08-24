"""Output models an toàn cho API phiên Agent."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.application.data_warehouse_workflows.output import AgentTurnKind
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import AgentResultStatus, SessionEventRole, SessionEventType, SessionStatus
from src.domain.project_session.value_objects import AgentResultMetadata
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ProjectSessionOutput:
    id: EntityID
    project_id: EntityID
    title: str
    status: SessionStatus
    is_running: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, session: ProjectSession) -> "ProjectSessionOutput":
        """Làm phẳng session, không lộ user nội bộ."""
        return cls(
            session.id,
            session.project_id,
            session.title,
            session.status,
            session.active_turn_id is not None,
            session.created_at,
            session.updated_at,
        )


@dataclass(frozen=True, slots=True)
class SessionEventOutput:
    id: EntityID
    session_id: EntityID
    turn_id: EntityID | None
    role: SessionEventRole
    type: SessionEventType
    content: str | None
    status: AgentResultStatus | None
    proposal_change_id: EntityID | None
    created_at: datetime

    @classmethod
    def from_domain(cls, event: SessionEvent) -> "SessionEventOutput":
        """Chỉ xuất metadata cần cho presentation."""
        metadata = event.metadata
        status = metadata.status if isinstance(metadata, AgentResultMetadata) else None
        proposal_id = _proposal_id(metadata)
        return cls(
            event.id,
            event.session_id,
            event.turn_id,
            event.role,
            event.type,
            event.content,
            status,
            proposal_id,
            event.created_at,
        )


@dataclass(frozen=True, slots=True)
class SessionTurnOutput:
    session_id: EntityID
    turn_id: EntityID
    kind: AgentTurnKind
    question: str | None = None
    proposal_change_id: EntityID | None = None
    summary: str | None = None


def _proposal_id(metadata: object) -> UUID | None:
    """Đọc UUID proposal từ Agent result mà không phát output thô."""
    if not isinstance(metadata, AgentResultMetadata) or not metadata.output_data:
        return None
    try:
        return UUID(metadata.output_data)
    except ValueError:
        return None
