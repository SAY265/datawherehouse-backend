"""Module quản lý Phiên Agent (Agent Session Domain)."""

from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    AgentType,
    SessionEventRole,
    SessionEventType,
    SessionStatus,
    ToolResultStatus,
)
from src.domain.project_session.repository import IProjectSessionRepository, ISessionEventRepository
from src.domain.project_session.rules import validate_session_event
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    LLMCallStats,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)

__all__: list[str] = [
    "ProjectSession",
    "SessionEvent",
    "SessionStatus",
    "SessionEventRole",
    "SessionEventType",
    "AgentType",
    "AgentResultStatus",
    "ToolResultStatus",
    "SessionEventMetadata",
    "MessageMetadata",
    "AgentCallMetadata",
    "AgentResultMetadata",
    "ToolCallMetadata",
    "ToolResultMetadata",
    "LLMCallStats",
    "IProjectSessionRepository",
    "ISessionEventRepository",
    "validate_session_event",
]
