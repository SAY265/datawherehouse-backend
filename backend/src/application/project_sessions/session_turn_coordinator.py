"""Coordinates one persisted Agent turn for a project session."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.input import CreateAgentTurnInput
from src.application.project_sessions.input import SendSessionMessageInput
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_access import OwnedSessionAccess
from src.application.project_sessions.session_event_factory import (
    UserEventInput,
    create_agent_call,
    create_user_event,
)
from src.application.project_sessions.session_turn_completion import (
    SessionTurnCompletion,
    TurnCompletionDependencies,
)
from src.application.project_sessions.session_turn_history import (
    TURN_STALE_AFTER,
    create_conversation,
    create_stale_turn_event,
)
from src.common.utils.datetime import utc_now
from src.common.utils.uuid import generate_uuid
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionEventType
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ISessionEventRepository,
)


@dataclass(frozen=True, slots=True)
class SessionTurnDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    workflow: IDataWarehouseWorkflowService
    unit_of_work: IUnitOfWork
    access: OwnedSessionAccess


class SessionTurnCoordinator:
    def __init__(self, dependencies: SessionTurnDependencies) -> None:
        self._dependencies = dependencies
        self._completion = SessionTurnCompletion(
            TurnCompletionDependencies(
                dependencies.sessions,
                dependencies.events,
                dependencies.unit_of_work,
            )
        )

    async def send(self, data: SendSessionMessageInput) -> SessionTurnOutput:
        session, history, call = await self._begin(data)
        try:
            result = await self._dependencies.workflow.create_agent_turn(
                CreateAgentTurnInput(
                    session.project_id,
                    data.content,
                    create_conversation(history),
                    turn_id=call.turn_id,
                )
            )
        except Exception:
            await self._completion.fail(session, call)
            raise
        return await self._completion.complete(session, call, result)

    async def _begin(
        self, data: SendSessionMessageInput
    ) -> tuple[ProjectSession, list[SessionEvent], SessionEvent]:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            session = await dependencies.access.require(
                data.session_id, for_update=True
            )
            history = await dependencies.events.list_by_session(
                session.id, limit=200
            )
            call = await self._persist_start(session, data.content, history)
            await dependencies.unit_of_work.commit()
        return session, history, call

    async def _persist_start(
        self,
        session: ProjectSession,
        content: str,
        history: list[SessionEvent],
    ) -> SessionEvent:
        turn_id = generate_uuid()
        stale_event = create_stale_turn_event(session, history)
        session.acquire_turn(turn_id, utc_now() - TURN_STALE_AFTER)
        is_answer = bool(
            history and history[-1].type is SessionEventType.QUESTION
        )
        call = create_agent_call(session.id, turn_id)
        await self._dependencies.sessions.save(session)
        if stale_event:
            await self._dependencies.events.save(stale_event)
        await self._dependencies.events.save(
            create_user_event(UserEventInput(session.id, turn_id, content, is_answer))
        )
        await self._dependencies.events.save(call)
        return call
