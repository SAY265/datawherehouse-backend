"""Persists the public result of an Agent turn."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    AgentTurnOutput,
)
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_event_factory import (
    AgentResultEventInput,
    create_agent_result,
    create_question,
)
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import AgentResultStatus
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ISessionEventRepository,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class TurnCompletionDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    unit_of_work: IUnitOfWork


class SessionTurnCompletion:
    def __init__(self, dependencies: TurnCompletionDependencies) -> None:
        self._dependencies = dependencies

    async def fail(
        self, session: ProjectSession, call: SessionEvent
    ) -> None:
        await self._finish(
            session,
            call.turn_id,
            create_agent_result(AgentResultEventInput(
                call, AgentResultStatus.FAILED, "Agent could not complete this turn."
            )),
        )

    async def complete(
        self,
        session: ProjectSession,
        call: SessionEvent,
        result: AgentTurnOutput,
    ) -> SessionTurnOutput:
        if result.kind is AgentTurnKind.CLARIFICATION:
            return await self._complete_question(session, call, result)
        change_id = result.proposal.summary.id if result.proposal else None
        event = create_agent_result(AgentResultEventInput(
            call,
            AgentResultStatus.SUCCESS,
            result.summary or "The proposal is ready for review.",
            str(change_id) if change_id else None,
        ))
        await self._finish(session, call.turn_id, event)
        return SessionTurnOutput(
            session.id,
            call.turn_id,
            result.kind,
            proposal_change_id=change_id,
            summary=result.summary,
        )

    async def _complete_question(
        self,
        session: ProjectSession,
        call: SessionEvent,
        result: AgentTurnOutput,
    ) -> SessionTurnOutput:
        question = result.question or "Please provide more information."
        await self._finish(
            session,
            call.turn_id,
            create_question(session.id, call.turn_id, question),
        )
        return SessionTurnOutput(
            session.id,
            call.turn_id,
            result.kind,
            question=question,
            summary=result.summary,
        )

    async def _finish(
        self,
        session: ProjectSession,
        turn_id: EntityID | None,
        event: SessionEvent,
    ) -> None:
        if turn_id is None:
            return
        session.release_turn(turn_id)
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            await dependencies.events.save(event)
            await dependencies.sessions.save(session)
            await dependencies.unit_of_work.commit()
