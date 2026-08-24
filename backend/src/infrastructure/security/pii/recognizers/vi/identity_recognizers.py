"""Recognizer CCCD và CMND Việt Nam yêu cầu ngữ cảnh rõ ràng."""

from src.infrastructure.security.pii.pii_entities import VN_CCCD, VN_CMND
from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.context_pattern_recognizer import (
    ContextPatternConfiguration,
    ContextPatternRecognizer,
)

IDENTITY_CONTEXT = (
    "cccd",
    "cmnd",
    "căn cước",
    "căn cước công dân",
    "chứng minh nhân dân",
    "số định danh",
)


def build_vietnamese_identity_recognizers() -> RecognizerCollection:
    """Tạo recognizer CCCD/CMND với validation và context scoring."""
    return (_build_cccd_recognizer(), _build_cmnd_recognizer())


def _build_cccd_recognizer() -> ContextPatternRecognizer:
    """Tạo recognizer CCCD 12 chữ số."""
    configuration = ContextPatternConfiguration(
        name="Vietnamese CCCD Recognizer",
        entity_type=VN_CCCD,
        language="vi",
        pattern=r"(?<!\d)(?P<value>\d{12})(?!\d)",
        context_words=IDENTITY_CONTEXT,
        base_score=0.2,
        contextual_score=0.85,
        validator=_is_plausible_cccd,
    )
    return ContextPatternRecognizer(configuration)


def _build_cmnd_recognizer() -> ContextPatternRecognizer:
    """Tạo recognizer CMND 9 chữ số."""
    configuration = ContextPatternConfiguration(
        name="Vietnamese CMND Recognizer",
        entity_type=VN_CMND,
        language="vi",
        pattern=r"(?<!\d)(?P<value>\d{9})(?!\d)",
        context_words=IDENTITY_CONTEXT,
        base_score=0.2,
        contextual_score=0.8,
        validator=_is_nonzero_number,
    )
    return ContextPatternRecognizer(configuration)


def _is_plausible_cccd(value: str) -> bool:
    """Loại mã số không thể là CCCD trước khi xét context."""
    province_code = int(value[:3])
    return 1 <= province_code <= 96 and _is_nonzero_number(value)


def _is_nonzero_number(value: str) -> bool:
    """Loại chuỗi toàn số 0 vì không thể là định danh hợp lệ."""
    return any(character != "0" for character in value)
