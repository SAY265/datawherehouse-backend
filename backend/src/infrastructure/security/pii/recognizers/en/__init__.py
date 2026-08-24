"""Recognizer mặc định cho văn bản tiếng Anh."""

from presidio_analyzer.predefined_recognizers import PhoneRecognizer
from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.common_recognizers import (
    build_common_recognizers,
)


def build_english_recognizers() -> RecognizerCollection:
    """Tạo built-in recognizer phù hợp cho tiếng Anh."""
    return (
        *build_common_recognizers("en"),
        PhoneRecognizer(
            supported_language="en",
            supported_regions=("US", "GB", "CA"),
        ),
    )
