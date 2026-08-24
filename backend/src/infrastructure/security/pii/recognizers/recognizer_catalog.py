"""Cấu hình provider recognizer mặc định theo ngôn ngữ."""

from collections.abc import Callable, Mapping
from types import MappingProxyType

from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.en import build_english_recognizers
from src.infrastructure.security.pii.recognizers.ja import build_japanese_recognizers
from src.infrastructure.security.pii.recognizers.vi import build_vietnamese_recognizers

RecognizerFactory = Callable[[], RecognizerCollection]

DEFAULT_RECOGNIZER_CATALOG: Mapping[str, RecognizerFactory] = MappingProxyType(
    {
        "en": build_english_recognizers,
        "ja": build_japanese_recognizers,
        "vi": build_vietnamese_recognizers,
    }
)


def build_catalog_recognizers(languages: tuple[str, ...]) -> RecognizerCollection:
    """Tạo recognizer cho các language có provider trong catalog."""
    recognizers = []
    for language in languages:
        factory = DEFAULT_RECOGNIZER_CATALOG.get(language)
        if factory:
            recognizers.extend(factory())
    return tuple(recognizers)
