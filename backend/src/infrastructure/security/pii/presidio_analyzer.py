"""Adapter phát hiện PII qua Microsoft Presidio Analyzer."""

from presidio_analyzer import AnalyzerEngine, EntityRecognizer
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.security.pii.language_configuration import (
    PiiLanguageConfiguration,
)
from src.infrastructure.security.pii.pii_detection import PiiDetection
from src.infrastructure.security.pii.recognizer_registry import PiiRecognizerRegistry


class PresidioPiiAnalyzer:
    """Phát hiện PII đa ngôn ngữ và không để model Presidio thoát ra ngoài."""

    def __init__(
        self,
        engine: AnalyzerEngine,
        configuration: PiiLanguageConfiguration,
        registry: PiiRecognizerRegistry,
    ) -> None:
        """Lưu các component analyzer dùng chung giữa nhiều request."""
        self._engine = engine
        self._configuration = configuration
        self._registry = registry

    def detect(
        self,
        text: str,
        language: str | None = None,
        entities: tuple[str, ...] | None = None,
    ) -> tuple[PiiDetection, ...]:
        """Phát hiện PII theo language và entity được yêu cầu.

        Raises:
            InfrastructureException: Khi cấu hình hoặc Presidio analyzer lỗi.
        """
        if not text:
            return ()
        try:
            results = self._engine.analyze(
                text=text,
                language=self._configuration.resolve(language),
                entities=list(entities) if entities else None,
                score_threshold=self._configuration.score_threshold,
            )
        except (TypeError, ValueError) as exc:
            raise _pii_error("Không thể phân tích thông tin cá nhân.") from exc
        return tuple(
            PiiDetection(result.entity_type, result.start, result.end, result.score)
            for result in results
        )

    def register_recognizer(self, recognizer: EntityRecognizer) -> None:
        """Đăng ký recognizer plugin vào analyzer đang dùng chung."""
        try:
            self._registry.register(recognizer)
        except (TypeError, ValueError) as exc:
            raise _pii_error("Không thể đăng ký bộ nhận diện PII.") from exc


def _pii_error(message: str) -> InfrastructureException:
    """Tạo lỗi hạ tầng đã loại bỏ chi tiết nội bộ của Presidio."""
    return InfrastructureException(code=ErrorCode.EXTERNAL_SERVICE_ERROR, message=message)
