"""Built-in Presidio recognizer dùng chung cho nhiều ngôn ngữ."""

from presidio_analyzer.predefined_recognizers import CreditCardRecognizer
from src.infrastructure.security.pii.recognizers import RecognizerCollection
from src.infrastructure.security.pii.recognizers.offline_email_recognizer import (
    OfflineEmailRecognizer,
)


def build_common_recognizers(language: str) -> RecognizerCollection:
    """Tạo recognizer email và thẻ có validation tích hợp của Presidio."""
    return (
        OfflineEmailRecognizer(supported_language=language),
        CreditCardRecognizer(supported_language=language),
    )
