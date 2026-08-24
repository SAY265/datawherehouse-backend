"""Orchestration core của PII masking framework."""

from presidio_analyzer import EntityRecognizer
from src.common.logging import get_logger
from src.infrastructure.security.pii.masking_policy import (
    DEFAULT_MASKING_POLICY,
    PiiMaskingPolicy,
)
from src.infrastructure.security.pii.pii_detection import PiiDetection
from src.infrastructure.security.pii.presidio_analyzer import PresidioPiiAnalyzer
from src.infrastructure.security.pii.presidio_anonymizer import PresidioPiiAnonymizer

logger = get_logger(__name__)


class PresidioPiiMaskingService:
    """Điều phối analyzer và anonymizer mà không chứa rule theo ngôn ngữ."""

    def __init__(
        self,
        analyzer: PresidioPiiAnalyzer,
        anonymizer: PresidioPiiAnonymizer,
        default_policy: PiiMaskingPolicy = DEFAULT_MASKING_POLICY,
    ) -> None:
        """Khởi tạo service từ các adapter đã được dựng một lần."""
        self._analyzer = analyzer
        self._anonymizer = anonymizer
        self._default_policy = default_policy

    def detect(
        self,
        text: str,
        language: str | None = None,
        entities: tuple[str, ...] | None = None,
    ) -> tuple[PiiDetection, ...]:
        """Phát hiện PII theo language và entity tùy chọn."""
        return self._analyzer.detect(text, language, entities)

    def mask(
        self,
        text: str,
        language: str | None = None,
        policy: PiiMaskingPolicy | None = None,
    ) -> str:
        """Phát hiện rồi anonymize các entity được policy cho phép."""
        selected_policy = policy or self._default_policy
        detections = self.detect(text, language, selected_policy.entities)
        masked = self._anonymizer.anonymize(text, detections, selected_policy)
        if detections:
            logger.info("pii_free_text_masked occurrences=%d", len(detections))
        return masked

    def register_recognizer(self, recognizer: EntityRecognizer) -> None:
        """Đăng ký plugin mới mà không thay đổi core masking flow."""
        self._analyzer.register_recognizer(recognizer)
