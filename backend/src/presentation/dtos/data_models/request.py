"""Request schemas và parameter constraints cho API Data Model."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError
from src.application.data_models.input import RunRelationshipAgentInput, UpdateDataModelInput
from src.common.exceptions.business import BusinessException
from src.domain.data_model.rules import validate_dbml

MAX_DBML_LENGTH = 1_000_000
ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa Data Model")]


class UpdateDataModelRequest(BaseModel):
    """Payload lưu snapshot DBML với revision gốc của client."""

    model_config = ConfigDict(extra="forbid")

    data_model_id: UUID = Field(description="ID của Data Model cần cập nhật")
    dbml: str = Field(
        min_length=1,
        max_length=MAX_DBML_LENGTH,
        description="Toàn bộ snapshot DBML mới",
    )
    base_revision: int = Field(
        ge=1,
        strict=True,
        description="Revision mà client đã tải trước khi chỉnh sửa",
    )

    @field_validator("dbml")
    @classmethod
    def validate_dbml_content(cls, value: str) -> str:
        """Kiểm tra đầy đủ nội dung DBML ngay tại HTTP request boundary."""
        try:
            validate_dbml(value)
        except BusinessException as exc:
            raise PydanticCustomError(
                exc.code.value,
                exc.message,
            ) from exc
        return value

    def to_application(self, project_id: UUID) -> UpdateDataModelInput:
        """Ánh xạ request DTO sang application input."""
        return UpdateDataModelInput(
            project_id=project_id,
            data_model_id=self.data_model_id,
            dbml=self.dbml,
            base_revision=self.base_revision,
        )


class RunRelationshipAgentRequest(BaseModel):
    """Bản nháp DBML hợp lệ cần Relationship Agent kiểm tra và tự nối."""

    model_config = ConfigDict(extra="forbid")

    dbml: str = Field(min_length=1, max_length=MAX_DBML_LENGTH)

    @field_validator("dbml")
    @classmethod
    def validate_dbml_content(cls, value: str) -> str:
        try:
            validate_dbml(value)
        except BusinessException as exc:
            raise PydanticCustomError(exc.code.value, exc.message) from exc
        return value

    def to_application(self, project_id: UUID) -> RunRelationshipAgentInput:
        return RunRelationshipAgentInput(project_id=project_id, dbml=self.dbml)


class DataModelChatRequest(BaseModel):
    """Payload gửi tin nhắn cho AI Chatbot trong Data Model."""

    message: str = Field(min_length=1, max_length=5000, description="Nội dung câu hỏi hoặc yêu cầu của người dùng")
    current_dbml: str = Field(default="", max_length=MAX_DBML_LENGTH, description="Snapshot DBML hiện tại trên editor")
    selected_table: str | None = Field(default=None, description="Bảng đang được chọn trên Canvas (nếu có)")
    history: list[dict[str, str]] | None = Field(default=None, description="Lịch sử hội thoại trước đó")
