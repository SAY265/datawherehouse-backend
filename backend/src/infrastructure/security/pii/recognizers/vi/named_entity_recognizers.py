"""Recognizer rule-based tạm thời cho PERSON và LOCATION tiếng Việt."""

from src.infrastructure.security.pii.pii_entities import LOCATION, PERSON
from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.context_pattern_recognizer import (
    ContextPatternConfiguration,
    ContextPatternRecognizer,
)

VIETNAMESE_NAME_PATTERN = (
    r"(?:họ\s+tên|tên|ông|bà|anh|chị)\s*[:\-]?\s*"
    r"(?P<value>[\p{Lu}][\p{L}'’-]+(?:\s+[\p{Lu}][\p{L}'’-]+){1,4})"
)
VIETNAMESE_LOCATION_PATTERN = (
    r"(?:địa\s*chỉ|nơi\s*ở)\s*[:\-]\s*"
    r"(?P<value>[^\n.;]{5,100})"
)


def build_vietnamese_named_entity_recognizers() -> RecognizerCollection:
    """Tạo fallback PERSON/LOCATION; NLP recognizer có thể thay thế về sau."""
    return (_build_person_recognizer(), _build_location_recognizer())


def _build_person_recognizer() -> ContextPatternRecognizer:
    """Tạo fallback recognizer cho tên người có label."""
    configuration = ContextPatternConfiguration(
        name="Vietnamese Person Context Recognizer",
        entity_type=PERSON,
        language="vi",
        pattern=VIETNAMESE_NAME_PATTERN,
        context_words=("họ tên", "tên", "ông", "bà", "anh", "chị"),
        base_score=0.2,
        contextual_score=0.78,
    )
    return ContextPatternRecognizer(configuration)


def _build_location_recognizer() -> ContextPatternRecognizer:
    """Tạo fallback recognizer cho địa chỉ có label."""
    configuration = ContextPatternConfiguration(
        name="Vietnamese Location Context Recognizer",
        entity_type=LOCATION,
        language="vi",
        pattern=VIETNAMESE_LOCATION_PATTERN,
        context_words=("địa chỉ", "nơi ở"),
        base_score=0.2,
        contextual_score=0.8,
    )
    return ContextPatternRecognizer(configuration)
