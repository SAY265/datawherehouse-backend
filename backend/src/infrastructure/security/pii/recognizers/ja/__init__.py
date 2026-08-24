"""Recognizer mặc định cho văn bản tiếng Nhật."""

from presidio_analyzer.predefined_recognizers import PhoneRecognizer
from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.common_recognizers import (
    build_common_recognizers,
)


def build_japanese_recognizers() -> RecognizerCollection:
    """Tạo built-in recognizer phù hợp cho tiếng Nhật."""
    return (
        *build_common_recognizers("ja"),
        PhoneRecognizer(supported_language="ja", supported_regions=("JP",)),
    )
