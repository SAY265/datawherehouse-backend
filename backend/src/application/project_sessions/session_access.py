"""Ownership checks shared by session query and turn commands."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.shared.types import EntityID


class OwnedSessionAccess:
    def __init__(
        self,
        sessions: IProjectSessionRepository,
        projects: ProjectAccessPolicy,
    ) -> None:
        self._sessions = sessions
        self._projects = projects

    async def require(
        self, session_id: EntityID, *, for_update: bool = False
    ) -> ProjectSession:
        session = (
            await self._sessions.get_by_id_for_update(session_id)
            if for_update
            else await self._sessions.get_by_id(session_id)
        )
        if session is None:
            raise BusinessException(
                ErrorCode.SESSION_NOT_FOUND,
                "Agent session was not found.",
            )
        await self._projects.require_owner(session.project_id)
        if session.user_id != self._projects.actor_id:
            raise BusinessException(
                ErrorCode.PERMISSION_DENIED,
                "You do not own this Agent session.",
            )
        return session
