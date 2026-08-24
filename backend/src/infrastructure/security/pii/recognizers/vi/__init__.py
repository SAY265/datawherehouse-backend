"""Recognizer mặc định cho văn bản tiếng Việt."""

from presidio_analyzer.predefined_recognizers import PhoneRecognizer
from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.common_recognizers import (
    build_common_recognizers,
)
from src.infrastructure.security.pii.recognizers.vi.identity_recognizers import (
    build_vietnamese_identity_recognizers,
)
from src.infrastructure.security.pii.recognizers.vi.named_entity_recognizers import (
    build_vietnamese_named_entity_recognizers,
)


def build_vietnamese_recognizers() -> RecognizerCollection:
    """Tạo recognizer chung và đặc thù Việt Nam."""
    return (
        *build_common_recognizers("vi"),
        PhoneRecognizer(supported_language="vi", supported_regions=("VN",)),
        *build_vietnamese_identity_recognizers(),
        *build_vietnamese_named_entity_recognizers(),
    )
