"""Interface cho AI Chatbot Service trong Data Model."""

from typing import Protocol

from src.application.data_models.input import DataModelChatInput
from src.application.data_models.output import DataModelChatOutput


class IDataModelChatService(Protocol):
    """Interface định nghĩa hợp đồng xử lý trò chuyện với AI Copilot trong Data Model."""

    async def chat(self, input: DataModelChatInput) -> DataModelChatOutput:
        """Xử lý tin nhắn hỏi đáp, phân tích schema và sinh đề xuất chỉnh sửa mô hình."""
        ...
