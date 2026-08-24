"""Facade tương thích cho che PII tại ranh giới gọi LLM."""

from presidio_analyzer import EntityRecognizer
from src.infrastructure.security.pii.factory import get_default_pii_masking_service
from src.infrastructure.security.pii.masking_policy import PiiMaskingPolicy
from src.infrastructure.security.pii.masking_service import PresidioPiiMaskingService
from src.infrastructure.security.pii.pii_detection import PiiDetection
from src.infrastructure.security.schema_identifier_masker import (
    MaskedPayload,
    SchemaIdentifierMasker,
)
from src.infrastructure.security.schema_identifier_patterns import PLACEHOLDER_PREFIX

__all__ = ["MaskedPayload", "PLACEHOLDER_PREFIX", "PiiGuard"]


class PiiGuard:
    """Facade giữ contract cũ và ủy quyền free-text cho Presidio."""

    def __init__(
        self,
        enabled: bool = True,
        masking_service: PresidioPiiMaskingService | None = None,
        default_language: str | None = None,
    ) -> None:
        """Khởi tạo guard từ masking service dùng chung."""
        self._enabled = enabled
        self._masking_service = masking_service or get_default_pii_masking_service()
        self._default_language = default_language
        self._schema_masker = SchemaIdentifierMasker()

    @property
    def enabled(self) -> bool:
        """Trả trạng thái guard."""
        return self._enabled

    def mask_schema(self, dbml: str) -> MaskedPayload:
        """Che tên cột nhạy cảm trong khai báo DBML."""
        if not self._enabled or not dbml:
            return MaskedPayload(dbml)
        return self._schema_masker.mask_schema(dbml)

    def mask_identifiers(self, text: str) -> MaskedPayload:
        """Che định danh nhạy cảm ở mọi vị trí trong văn bản."""
        if not self._enabled or not text:
            return MaskedPayload(text)
        return self._schema_masker.mask_identifiers(text)

    def detect_free_text(
        self,
        text: str,
        language: str | None = None,
        entities: tuple[str, ...] | None = None,
    ) -> tuple[PiiDetection, ...]:
        """Phát hiện PII trong văn bản tự do theo language."""
        if not self._enabled or not text:
            return ()
        return self._masking_service.detect(
            text,
            language or self._default_language,
            entities,
        )

    def mask_free_text(
        self,
        text: str,
        language: str | None = None,
        policy: PiiMaskingPolicy | None = None,
    ) -> str:
        """Che PII trong văn bản tự do bằng policy được chọn."""
        if not self._enabled or not text:
            return text
        return self._masking_service.mask(
            text,
            language or self._default_language,
            policy,
        )

    def register_recognizer(self, recognizer: EntityRecognizer) -> None:
        """Đăng ký Presidio recognizer plugin vào service hiện tại."""
        self._masking_service.register_recognizer(recognizer)

    def unmask(self, text: str, mapping: dict[str, str]) -> str:
        """Hoàn nguyên chính xác placeholder từ mapping của lời gọi."""
        return self._schema_masker.unmask(text, mapping)

    def has_residual_placeholder(self, text: str) -> bool:
        """Fail closed nếu LLM làm biến dạng placeholder chưa hoàn nguyên."""
        return self._schema_masker.has_residual_placeholder(text)
