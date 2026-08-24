"""Application service duy nhất của module Session."""

from src.application.sessions.i_session_service import ISessionService


class SessionService(ISessionService):
    """Điểm hiện thực tập trung cho các use case Session."""
