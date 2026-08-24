"""Domain entities & value objects cho AI Chatbot trong Data Modeling."""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class ChatMessage:
    """Đại diện cho một tin nhắn trong phiên chat với AI Assistant."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str | None = None


@dataclass(frozen=True)
class ChatProposedAction:
    """Đại diện cho một hành động thay đổi mô hình dữ liệu do AI đề xuất."""

    action_type: Literal["create_table", "add_column", "modify_table", "replace_dbml"]
    table_name: str
    title: str
    description: str
    preview_dbml: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatDataModelContext:
    """Ngữ cảnh của mô hình dữ liệu hiện hành gửi kèm theo tin nhắn."""

    current_dbml: str
    selected_table: str | None = None
    dialect: str = "postgresql"
