"""Quy tắc nghiệp vụ cho miền Phiên Agent (Agent Session)."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.types import EntityID


def validate_session_event(session_id: EntityID) -> None:
    """Kiểm tra tính hợp lệ của sự kiện thuộc về phiên làm việc."""
    if not session_id:
        raise BusinessException(
            code=ErrorCode.INVALID_SESSION_EVENT_REF,
            message="Sự kiện phiên làm việc phải thuộc về một session_id hợp lệ.",
        )
