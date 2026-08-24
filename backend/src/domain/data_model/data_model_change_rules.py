"""Quy tắc revision và vòng đời đề xuất thay đổi Data Model."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.enums import DataModelChangeStatus

INITIAL_DATA_MODEL_REVISION = 1
_ALLOWED_CHANGE_TRANSITIONS: dict[
    DataModelChangeStatus,
    frozenset[DataModelChangeStatus],
] = {
    DataModelChangeStatus.PROPOSED: frozenset(
        {
            DataModelChangeStatus.ACCEPTED,
            DataModelChangeStatus.REJECTED,
            DataModelChangeStatus.CONFLICTED,
        }
    ),
    DataModelChangeStatus.ACCEPTED: frozenset(),
    DataModelChangeStatus.REJECTED: frozenset(),
    DataModelChangeStatus.CONFLICTED: frozenset(),
}


def validate_revision(revision: int) -> None:
    """Bảo đảm revision là số nguyên dương.

    Args:
        revision: Revision cần kiểm tra.

    Raises:
        BusinessException: Khi revision nhỏ hơn revision khởi tạo.
    """
    if (
        not isinstance(revision, int)
        or isinstance(revision, bool)
        or revision < INITIAL_DATA_MODEL_REVISION
    ):
        raise BusinessException(
            code=ErrorCode.DATA_MODEL_REVISION_INVALID,
            message="Revision của Data Model phải là số nguyên dương.",
        )


def validate_revision_match(base_revision: int, current_revision: int) -> None:
    """Kiểm tra optimistic revision trước khi thay đổi Data Model.

    Args:
        base_revision: Revision mà caller đã đọc.
        current_revision: Revision hiện tại của aggregate.

    Raises:
        BusinessException: Khi hai revision không khớp.
    """
    if base_revision != current_revision:
        raise BusinessException(
            code=ErrorCode.DATA_MODEL_REVISION_CONFLICT,
            message=(
                f"Base revision ({base_revision}) không khớp revision hiện tại "
                f"({current_revision})."
            ),
        )


def validate_change_status_transition(
    current_status: DataModelChangeStatus,
    target_status: DataModelChangeStatus,
) -> None:
    """Kiểm tra state transition của đề xuất thay đổi Data Model.

    Args:
        current_status: Trạng thái hiện tại.
        target_status: Trạng thái muốn chuyển tới.

    Raises:
        BusinessException: Khi đề xuất đã kết thúc hoặc transition bị cấm.
    """
    if target_status not in _ALLOWED_CHANGE_TRANSITIONS[current_status]:
        raise BusinessException(
            code=ErrorCode.INVALID_DATA_MODEL_CHANGE_STATUS_TRANSITION,
            message=f"Không thể chuyển đề xuất từ '{current_status}' sang '{target_status}'.",
        )
