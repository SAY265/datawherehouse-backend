"""Quy tắc nghiệp vụ cho miền Mô hình Dữ liệu (Data Model)."""

from json import loads

try:
    from lark_dbml import loads
    from lark_dbml.lark_dbml_standalone import UnexpectedInput
except ImportError:
    loads = lambda s: None  # noqa: E731
    UnexpectedInput = Exception
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.enums import DataModelChangeStatus


def validate_dbml(dbml: str) -> None:
    """Kiểm tra nội dung và cú pháp DBML.

    Args:
        dbml: Nội dung DBML cần xác thực.

    Raises:
        BusinessException: Khi cú pháp DBML không hợp lệ.
    """
    if not dbml or not dbml.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_DBML_CONTENT,
            message="Nội dung DBML không được để trống.",
        )
    try:
        loads(dbml)
    except (UnexpectedInput, Exception) as exc:
        raise BusinessException(
            code=ErrorCode.INVALID_DBML_CONTENT,
            message="Nội dung DBML không hợp lệ.",
        ) from exc


def validate_revision_match(base_revision: int, current_revision: int) -> None:
    """Kiểm tra sự phù hợp revision khi áp dụng thay đổi (Optimistic Locking)."""
    if base_revision != current_revision:
        raise BusinessException(
            code=ErrorCode.REVISION_CONFLICT,
            message=(
                f"Xung đột revision (Conflict)! Base revision của đề xuất ({base_revision}) "
                f"không khớp với revision hiện tại của data model ({current_revision})."
            ),
        )


def validate_change_status_transition(
    current_status: DataModelChangeStatus,
    target_status: DataModelChangeStatus,
) -> None:
    """Kiểm tra luồng chuyển đổi trạng thái của DataModelChange."""
    if current_status != DataModelChangeStatus.PROPOSED:
        raise BusinessException(
            code=ErrorCode.INVALID_PROPOSAL_STATUS_TRANSITION,
            message=f"Thay đổi đang ở trạng thái '{current_status}' nên không thể chuyển sang '{target_status}'.",
        )
