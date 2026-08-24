"""Email recognizer Presidio dùng Public Suffix snapshot cục bộ."""

import tldextract
from presidio_analyzer.predefined_recognizers import EmailRecognizer
from typing_extensions import override


class OfflineEmailRecognizer(EmailRecognizer):
    """Giữ built-in email pattern nhưng cấm tải suffix list lúc runtime."""

    def __init__(self, supported_language: str) -> None:
        """Khởi tạo built-in recognizer và offline TLD validator."""
        super().__init__(supported_language=supported_language)
        self._extract = tldextract.TLDExtract(suffix_list_urls=())

    @override
    def validate_result(self, pattern_text: str) -> bool:
        """Xác thực email bằng Public Suffix snapshot đóng gói trong dependency."""
        return self._extract(pattern_text).fqdn != ""
