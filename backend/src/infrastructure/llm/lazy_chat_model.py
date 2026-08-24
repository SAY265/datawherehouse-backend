"""Lazy provider dùng chung cho các Agent adapter."""

from collections.abc import Callable

from langchain_core.language_models import BaseChatModel

ChatModelSource = BaseChatModel | Callable[[], BaseChatModel]


class LazyChatModel:
    """Chỉ khởi tạo chat model khi use case AI thực sự chạy."""

    def __init__(self, source: ChatModelSource) -> None:
        """Lưu model hoặc factory mà chưa gọi factory."""
        self._source = source
        self._model: BaseChatModel | None = None

    def get(self) -> BaseChatModel:
        """Trả model đã cache hoặc tạo model ở lần gọi đầu."""
        if self._model is None:
            self._model = self._source() if callable(self._source) else self._source
        return self._model
