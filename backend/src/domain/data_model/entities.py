"""Các thực thể thuộc miền Mô hình Dữ liệu (Data Model Entities)."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.common.exceptions.business import BusinessException
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_model.rules import (
    validate_change_status_transition,
    validate_dbml,
    validate_revision_match,
)
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass
class DataModel(BaseEntity):
    """Thực thể đại diện cho Mô hình Dữ liệu (Data Model)."""

    project_id: EntityID = field(default_factory=uuid4)
    dbml: str = ""
    revision: int = 1

    def __post_init__(self) -> None:
        """Thực thi kiểm tra quy tắc dữ liệu cho DataModel."""
        super().__post_init__()
        validate_dbml(self.dbml)

    def apply_change(self, change: "DataModelChange") -> None:
        """Áp dụng đề xuất thay đổi mô hình dữ liệu (Optimistic Concurrency Control)."""
        if change.status != DataModelChangeStatus.PROPOSED:
            validate_change_status_transition(change.status, DataModelChangeStatus.ACCEPTED)

        try:
            validate_revision_match(change.base_revision, self.revision)
        except BusinessException:
            change.mark_conflicted()
            raise

        self.dbml = change.proposed_dbml
        self.revision += 1
        self.mark_updated()
        change.mark_accepted()

    def update_dbml(self, dbml: str, base_revision: int) -> None:
        """Cập nhật snapshot DBML sau khi kiểm tra revision và cú pháp."""
        validate_revision_match(base_revision, self.revision)
        validate_dbml(dbml)
        self.dbml = dbml
        self.revision += 1
        self.mark_updated()


@dataclass
class DataModelChange(BaseEntity):
    """Thực thể đại diện cho Đề xuất Thay đổi Mô hình Dữ liệu (Data Model Change)."""

    data_model_id: EntityID = field(default_factory=uuid4)
    user_id: EntityID = field(default_factory=uuid4)
    base_revision: int = 1
    proposed_dbml: str = ""
    status: DataModelChangeStatus = DataModelChangeStatus.PROPOSED

    def __post_init__(self) -> None:
        """Thực thi kiểm tra quy tắc dữ liệu cho DataModelChange."""
        super().__post_init__()
        validate_dbml(self.proposed_dbml)

    def mark_accepted(self) -> None:
        """Đánh dấu đề xuất thay đổi đã được chấp nhận (ACCEPTED)."""
        validate_change_status_transition(self.status, DataModelChangeStatus.ACCEPTED)
        self.status = DataModelChangeStatus.ACCEPTED
        self.mark_updated()

    def mark_rejected(self) -> None:
        """Đánh dấu đề xuất thay đổi bị từ chối (REJECTED)."""
        validate_change_status_transition(self.status, DataModelChangeStatus.REJECTED)
        self.status = DataModelChangeStatus.REJECTED
        self.mark_updated()

    def mark_conflicted(self) -> None:
        """Đánh dấu đề xuất thay đổi bị xung đột revision (CONFLICTED)."""
        self.status = DataModelChangeStatus.CONFLICTED
        self.mark_updated()
