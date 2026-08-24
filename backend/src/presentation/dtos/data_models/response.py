"""Response schemas cho API Data Model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_models.output import (
    DataModelChatOutput,
    DataModelDdlOutput,
    DataModelInsightOutput,
    DataModelOutput,
    RelationshipAgentOutput,
)


class DataModelResponse(BaseModel):
    """Snapshot Data Model trả về cho Frontend editor."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID của Data Model")
    project_id: UUID = Field(description="ID dự án sở hữu Data Model")
    dbml: str = Field(min_length=1, description="Snapshot DBML hiện tại")
    revision: int = Field(ge=1, description="Revision phục vụ optimistic locking")
    created_at: datetime = Field(description="Thời điểm tạo theo ISO 8601")
    updated_at: datetime = Field(description="Thời điểm cập nhật theo ISO 8601")

    @classmethod
    def from_application(cls, output: DataModelOutput) -> "DataModelResponse":
        """Ánh xạ application output sang response DTO."""
        return cls.model_validate(output)


class DataModelDdlResponse(BaseModel):
    """DDL sinh từ revision Data Model hiện tại."""

    model_config = ConfigDict(from_attributes=True)

    ddl: str
    dialect: str
    revision: int = Field(ge=1)

    @classmethod
    def from_application(cls, output: DataModelDdlOutput) -> "DataModelDdlResponse":
        return cls.model_validate(output)


class DataModelInsightResponse(BaseModel):
    """Insight cấu trúc của một bảng trong Data Model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    table_name: str
    severity: str
    title: str
    description: str

    @classmethod
    def from_application(cls, output: DataModelInsightOutput) -> "DataModelInsightResponse":
        return cls.model_validate(output)


class RelationshipRefResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_table: str
    from_column: str
    to_table: str
    to_column: str


class RelationshipWarningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    message: str
    table_name: str
    column_name: str
    expected_table: str | None = None


class RelationshipAgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dbml: str
    added_relationships: list[RelationshipRefResponse]
    warnings: list[RelationshipWarningResponse]

    @classmethod
    def from_application(cls, output: RelationshipAgentOutput) -> "RelationshipAgentResponse":
        return cls.model_validate(output)


class ChatProposedActionResponse(BaseModel):
    """Hành động thay đổi schema do AI đề xuất."""

    model_config = ConfigDict(from_attributes=True)

    action_type: str
    table_name: str
    title: str
    description: str
    preview_dbml: str
    payload: dict


class DataModelChatResponse(BaseModel):
    """Phản hồi của AI Chatbot cho Frontend."""

    model_config = ConfigDict(from_attributes=True)

    reply: str
    actions: list[ChatProposedActionResponse]

    @classmethod
    def from_application(cls, output: DataModelChatOutput) -> "DataModelChatResponse":
        """Ánh xạ application output và các action lồng nhau sang response DTO."""
        return cls.model_validate(output)
