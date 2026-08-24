"""Input model cho các thao tác Data Model."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class GetDataModelInput:
    """Dữ liệu đầu vào để lấy Data Model hiện tại của dự án."""

    project_id: EntityID


@dataclass(frozen=True)
class UpdateDataModelInput:
    """Dữ liệu đầu vào để cập nhật Data Model bằng optimistic locking."""

    project_id: EntityID
    data_model_id: EntityID
    dbml: str
    base_revision: int


@dataclass(frozen=True)
class RunRelationshipAgentInput:
    """Bản nháp DBML cần tự nối quan hệ trong phạm vi một project."""

    project_id: EntityID
    dbml: str


@dataclass(frozen=True)
class DataModelChatInput:
    """Dữ liệu đầu vào cho yêu cầu trò chuyện AI Chatbot trong Data Model."""

    project_id: EntityID
    message: str
    current_dbml: str
    selected_table: str | None = None
    history: list[dict[str, str]] | None = None
