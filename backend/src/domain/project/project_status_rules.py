"""Quy tắc trạng thái của Project."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.enums import ProjectStatus

_ALLOWED_STATUS_TRANSITIONS: dict[ProjectStatus, frozenset[ProjectStatus]] = {
    ProjectStatus.ACTIVE: frozenset({ProjectStatus.ANALYZING, ProjectStatus.ARCHIVED}),
    ProjectStatus.ANALYZING: frozenset({ProjectStatus.ACTIVE}),
    ProjectStatus.ARCHIVED: frozenset({ProjectStatus.ACTIVE}),
}


def validate_project_editable(status: ProjectStatus) -> None:
    """Bảo đảm dự án đang ở trạng thái cho phép chỉnh sửa.

    Args:
        status: Trạng thái hiện tại của dự án.

    Raises:
        BusinessException: Khi dự án không ở trạng thái ACTIVE.
    """
    if status != ProjectStatus.ACTIVE:
        _raise("Chỉ dự án đang hoạt động mới được phép chỉnh sửa.")


def validate_status_transition(current: ProjectStatus, target: ProjectStatus) -> None:
    """Kiểm tra state transition của dự án.

    Args:
        current: Trạng thái hiện tại.
        target: Trạng thái đích.

    Raises:
        BusinessException: Khi transition không được tài liệu hóa.
    """
    if target not in _ALLOWED_STATUS_TRANSITIONS[current]:
        _raise(f"Không thể chuyển trạng thái dự án từ {current.value} sang {target.value}.")


def _raise(message: str) -> None:
    """Ném lỗi state transition thống nhất."""
    raise BusinessException(
        code=ErrorCode.INVALID_PROJECT_STATUS_TRANSITION,
        message=message,
    )
