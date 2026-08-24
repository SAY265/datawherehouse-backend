"""Factory duy nhất tạo event quan sát được của phiên Agent."""

from dataclasses import dataclass

from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import AgentResultStatus, AgentType, SessionEventRole, SessionEventType
from src.domain.project_session.value_objects import AgentCallMetadata, AgentResultMetadata
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class UserEventInput:
    session_id: EntityID
    turn_id: EntityID
    content: str
    is_answer: bool


@dataclass(frozen=True, slots=True)
class AgentResultEventInput:
    call: SessionEvent
    status: AgentResultStatus
    content: str
    output: str | None = None


def create_user_event(data: UserEventInput) -> SessionEvent:
    """Tạo message hoặc answer từ người dùng."""
    event_type = SessionEventType.ANSWER if data.is_answer else SessionEventType.MESSAGE
    return SessionEvent(
        session_id=data.session_id,
        turn_id=data.turn_id,
        role=SessionEventRole.USER,
        type=event_type,
        content=data.content,
    )


def create_agent_call(session_id: EntityID, turn_id: EntityID) -> SessionEvent:
    """Tạo mốc bắt đầu Agent không lưu raw prompt."""
    return SessionEvent(
        session_id=session_id,
        turn_id=turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_CALL,
        metadata=AgentCallMetadata(
            AgentType.ORCHESTRATOR,
            AgentType.DW_DESIGN,
            "session-conversation",
        ),
    )


def create_question(session_id: EntityID, turn_id: EntityID, question: str) -> SessionEvent:
    """Tạo câu hỏi làm rõ hiển thị cho người dùng."""
    return SessionEvent(
        session_id=session_id,
        turn_id=turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.QUESTION,
        content=question,
    )


def create_agent_result(data: AgentResultEventInput) -> SessionEvent:
    """Tạo kết quả Agent với metadata công khai tối thiểu."""
    return SessionEvent(
        session_id=data.call.session_id,
        turn_id=data.call.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_RESULT,
        content=data.content,
        metadata=AgentResultMetadata(
            AgentType.DW_DESIGN,
            data.status,
            data.call.id,
            output_data=data.output,
        ),
    )
