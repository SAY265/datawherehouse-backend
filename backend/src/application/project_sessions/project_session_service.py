"""Application service for persisted project Agent sessions."""

from dataclasses import dataclass

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.project_sessions.i_project_session_service import (
    IProjectSessionService,
)
from src.application.project_sessions.input import (
    CreateSessionInput,
    GetSessionInput,
    ListSessionEventsInput,
    ListSessionsInput,
    RenameSessionInput,
    SendSessionMessageInput,
)
from src.application.project_sessions.output import (
    ProjectSessionOutput,
    SessionEventOutput,
    SessionTurnOutput,
)
from src.application.project_sessions.session_access import OwnedSessionAccess
from src.application.project_sessions.session_turn_coordinator import (
    SessionTurnCoordinator,
    SessionTurnDependencies,
)
from src.domain.project_session.entities import DEFAULT_SESSION_TITLE, ProjectSession
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ISessionEventRepository,
)
from typing_extensions import override


@dataclass(frozen=True, slots=True)
class ProjectSessionDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    workflow: IDataWarehouseWorkflowService
    unit_of_work: IUnitOfWork
    access: ProjectAccessPolicy


class ProjectSessionService(IProjectSessionService):
    def __init__(self, dependencies: ProjectSessionDependencies) -> None:
        self._sessions = dependencies.sessions
        self._events = dependencies.events
        self._unit_of_work = dependencies.unit_of_work
        self._projects = dependencies.access
        self._access = OwnedSessionAccess(
            dependencies.sessions, dependencies.access
        )
        self._turns = SessionTurnCoordinator(
            SessionTurnDependencies(
                dependencies.sessions,
                dependencies.events,
                dependencies.workflow,
                dependencies.unit_of_work,
                self._access,
            )
        )

    @override
    async def create_session(
        self, data: CreateSessionInput
    ) -> ProjectSessionOutput:
        await self._projects.require_owner(data.project_id)
        session = ProjectSession(
            project_id=data.project_id,
            user_id=self._projects.actor_id,
            title=data.title or DEFAULT_SESSION_TITLE,
        )
        async with self._unit_of_work:
            saved = await self._sessions.save(session)
            await self._unit_of_work.commit()
        return ProjectSessionOutput.from_domain(saved)

    @override
    async def list_sessions(
        self, data: ListSessionsInput
    ) -> tuple[ProjectSessionOutput, ...]:
        await self._projects.require_owner(data.project_id)
        sessions = await self._sessions.list_by_project_user(
            data.project_id, self._projects.actor_id
        )
        return tuple(ProjectSessionOutput.from_domain(item) for item in sessions)

    @override
    async def get_session(self, data: GetSessionInput) -> ProjectSessionOutput:
        session = await self._access.require(data.session_id)
        return ProjectSessionOutput.from_domain(session)

    @override
    async def rename_session(self, data: RenameSessionInput) -> ProjectSessionOutput:
        session = await self._access.require(data.session_id)
        session.rename(data.title)
        async with self._unit_of_work:
            saved = await self._sessions.save(session)
            await self._unit_of_work.commit()
        return ProjectSessionOutput.from_domain(saved)

    @override
    async def list_events(
        self, data: ListSessionEventsInput
    ) -> tuple[SessionEventOutput, ...]:
        await self._access.require(data.session_id)
        events = await self._events.list_by_session(
            data.session_id, data.after_id, data.limit
        )
        return tuple(SessionEventOutput.from_domain(item) for item in events)

    @override
    async def send_message(
        self, data: SendSessionMessageInput
    ) -> SessionTurnOutput:
        return await self._turns.send(data)
