"""Thực thể đề xuất thay đổi Data Model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.data_model_change_rules import (
    INITIAL_DATA_MODEL_REVISION,
    validate_change_status_transition,
    validate_revision,
)
from src.domain.data_model.dbml_syntax_rules import validate_dbml
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID

if TYPE_CHECKING:
    from src.domain.data_model.entities import DataModel


@dataclass(eq=False, kw_only=True)
class DataModelChange(BaseEntity):
    """Đề xuất thay đổi có lifecycle và optimistic base revision."""

    data_model_id: EntityID
    user_id: EntityID
    base_revision: int = INITIAL_DATA_MODEL_REVISION
    base_dbml: str
    proposed_dbml: str
    status: DataModelChangeStatus = DataModelChangeStatus.PROPOSED

    def __post_init__(self) -> None:
        """Chuẩn hóa trạng thái và kiểm tra dữ liệu đề xuất."""
        super().__post_init__()
        self.status = normalize_str_enum(
            self.status,
            DataModelChangeStatus,
            ErrorCode.INVALID_DATA_MODEL_CHANGE_STATUS_TRANSITION,
        )
        validate_revision(self.base_revision)
        validate_dbml(self.base_dbml)
        validate_dbml(self.proposed_dbml)

    def mark_accepted(self) -> None:
        """Chuyển đề xuất từ PROPOSED sang ACCEPTED."""
        self._transition_to(DataModelChangeStatus.ACCEPTED)

    def mark_rejected(self) -> None:
        """Chuyển đề xuất từ PROPOSED sang REJECTED."""
        self._transition_to(DataModelChangeStatus.REJECTED)

    def mark_conflicted(self) -> None:
        """Chuyển đề xuất từ PROPOSED sang CONFLICTED."""
        self._transition_to(DataModelChangeStatus.CONFLICTED)

    def replace_proposal(
        self,
        proposed_dbml: str,
        model: DataModel,
    ) -> None:
        """Thay nội dung của đề xuất vẫn đang chờ xử lý.

        Args:
            proposed_dbml: Snapshot DBML mới.
            model: Data Model hiện hành làm căn cứ.

        Raises:
            BusinessException: Khi trạng thái hoặc nội dung không hợp lệ.
        """
        if self.status != DataModelChangeStatus.PROPOSED:
            raise BusinessException(
                code=ErrorCode.INVALID_DATA_MODEL_CHANGE_STATUS_TRANSITION,
                message=f"Không thể thay đề xuất ở trạng thái '{self.status}'.",
            )
        base_revision = model.revision
        validate_revision(base_revision)
        validate_dbml(proposed_dbml)
        self.proposed_dbml = proposed_dbml
        self.base_revision = base_revision
        self.base_dbml = model.dbml
        self.mark_updated()

    def _transition_to(self, target: DataModelChangeStatus) -> None:
        """Áp dụng transition hợp lệ và cập nhật timestamp."""
        validate_change_status_transition(self.status, target)
        self.status = target
        self.mark_updated()
