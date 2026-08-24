"""Output model cho các thao tác Data Model."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.data_model.entities import DataModel
from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class DataModelOutput:
    """Snapshot Data Model được phép đi qua application boundary."""

    id: EntityID
    project_id: EntityID
    dbml: str
    revision: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, data_model: DataModel) -> "DataModelOutput":
        """Ánh xạ domain entity sang application output."""
        return cls(
            id=data_model.id,
            project_id=data_model.project_id,
            dbml=data_model.dbml,
            revision=data_model.revision,
            created_at=data_model.created_at,
            updated_at=data_model.updated_at,
        )


@dataclass(frozen=True)
class DataModelDdlOutput:
    """DDL được sinh từ một revision Data Model cụ thể."""

    ddl: str
    dialect: str
    revision: int


@dataclass(frozen=True)
class DataModelInsightOutput:
    """Một nhận xét cấu trúc được sinh từ DBML hiện tại."""

    id: str
    table_name: str
    severity: str
    title: str
    description: str


@dataclass(frozen=True)
class RelationshipRefOutput:
    from_table: str
    from_column: str
    to_table: str
    to_column: str


@dataclass(frozen=True)
class RelationshipWarningOutput:
    code: str
    message: str
    table_name: str
    column_name: str
    expected_table: str | None


@dataclass(frozen=True)
class RelationshipAgentOutput:
    """DBML đã nối cùng báo cáo minh bạch về các quan hệ còn thiếu."""

    dbml: str
    added_relationships: list[RelationshipRefOutput]
    warnings: list[RelationshipWarningOutput]


@dataclass(frozen=True)
class ChatProposedActionOutput:
    """Hành động thay đổi mô hình do Chatbot đề xuất."""

    action_type: str
    table_name: str
    title: str
    description: str
    preview_dbml: str
    payload: dict


@dataclass(frozen=True)
class DataModelChatOutput:
    """Kết quả phản hồi từ AI Chatbot."""

    reply: str
    actions: list[ChatProposedActionOutput]
