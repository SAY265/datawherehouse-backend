"""Builds safe Agent history and detects abandoned turns."""

from datetime import timedelta

from src.application.data_warehouse_workflows.input import ConversationMessage
from src.application.project_sessions.session_event_factory import (
    AgentResultEventInput,
    create_agent_result,
)
from src.common.utils.datetime import utc_now
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    SessionEventRole,
    SessionEventType,
)

TURN_STALE_AFTER = timedelta(minutes=15)


def create_conversation(
    events: list[SessionEvent],
) -> tuple[ConversationMessage, ...]:
    visible = (
        event
        for event in events
        if event.content
        and event.role in {SessionEventRole.USER, SessionEventRole.AGENT}
    )
    return tuple(
        ConversationMessage(event.role.value.lower(), event.content or "")
        for event in visible
    )


def create_stale_turn_event(
    session: ProjectSession,
    events: list[SessionEvent],
) -> SessionEvent | None:
    if not session.active_turn_id or not session.active_turn_started_at:
        return None
    if session.active_turn_started_at >= utc_now() - TURN_STALE_AFTER:
        return None
    call = next(
        (
            event
            for event in reversed(events)
            if event.turn_id == session.active_turn_id
            and event.type is SessionEventType.AGENT_CALL
        ),
        None,
    )
    return (
        create_agent_result(AgentResultEventInput(
            call, AgentResultStatus.FAILED, "Agent turn timed out before completion."
        ))
        if call
        else None
    )
