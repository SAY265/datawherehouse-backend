"""Registry mở rộng recognizer mà không sửa PII masking service."""

from collections.abc import Iterable

from presidio_analyzer import EntityRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngine, NoOpNlpEngine
from src.infrastructure.security.pii.language_configuration import (
    PiiLanguageConfiguration,
)


class PiiRecognizerRegistry:
    """Bọc Presidio registry và bảo vệ cấu hình language nhất quán."""

    def __init__(
        self,
        configuration: PiiLanguageConfiguration,
        recognizers: Iterable[EntityRecognizer],
    ) -> None:
        """Khởi tạo registry và đăng ký các plugin ban đầu."""
        self._configuration = configuration
        self._registry = RecognizerRegistry(
            supported_languages=list(configuration.supported_languages)
        )
        for recognizer in recognizers:
            self.register(recognizer)

    @property
    def presidio_registry(self) -> RecognizerRegistry:
        """Trả registry cho AnalyzerEngine tại Infrastructure boundary."""
        return self._registry

    def register(self, recognizer: EntityRecognizer) -> None:
        """Đăng ký recognizer mới sau khi kiểm tra language hỗ trợ.

        Args:
            recognizer: Presidio recognizer plugin cần bổ sung.

        Raises:
            ValueError: Khi recognizer dùng language chưa cấu hình.
        """
        self._configuration.resolve(recognizer.supported_language)
        self._registry.add_recognizer(recognizer)

    def register_nlp_engine(self, nlp_engine: NlpEngine) -> None:
        """Gắn NER recognizer từ NLP engine tùy chọn."""
        if not isinstance(nlp_engine, NoOpNlpEngine):
            self._registry.add_nlp_recognizer(nlp_engine)
