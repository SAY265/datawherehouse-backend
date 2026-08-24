"""Quản lý ngữ cảnh request và agent tracing qua ContextVars (Async / Thread-safe)."""

from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
session_id_ctx: ContextVar[str | None] = ContextVar("session_id", default=None)
agent_name_ctx: ContextVar[str | None] = ContextVar("agent_name", default=None)


def get_request_id() -> str | None:
    """Lấy request ID của request hiện tại."""
    return request_id_ctx.get()


def set_request_id(request_id: str | None) -> None:
    """Ghi nhận request ID cho ngữ cảnh hiện tại."""
    request_id_ctx.set(request_id)


def get_correlation_id() -> str | None:
    """Lấy correlation ID (nếu có) cho luồng truy vết đa hệ thống."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str | None) -> None:
    """Ghi nhận correlation ID cho ngữ cảnh hiện tại."""
    correlation_id_ctx.set(correlation_id)


def get_session_id() -> str | None:
    """Lấy session ID của người dùng/hội thoại hiện tại."""
    return session_id_ctx.get()


def set_session_id(session_id: str | None) -> None:
    """Ghi nhận session ID cho ngữ cảnh hiện tại."""
    session_id_ctx.set(session_id)


def get_agent_name() -> str | None:
    """Lấy tên Agent đang thực thi trong luồng Multi-Agent."""
    return agent_name_ctx.get()


def set_agent_name(agent_name: str | None) -> None:
    """Ghi nhận tên Agent cho ngữ cảnh hiện tại."""
    agent_name_ctx.set(agent_name)


def clear_logging_context() -> None:
    """Xóa toàn bộ ngữ cảnh logging sau khi hoàn thành request hoặc task."""
    request_id_ctx.set(None)
    correlation_id_ctx.set(None)
    session_id_ctx.set(None)
    agent_name_ctx.set(None)
