"""Cấu hình ngôn ngữ và ngưỡng tin cậy cho PII analyzer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PiiLanguageConfiguration:
    """Cấu hình các ngôn ngữ được phép dùng trong một analyzer dùng chung."""

    supported_languages: tuple[str, ...] = ("vi", "en", "ja")
    default_language: str = "vi"
    score_threshold: float = 0.4

    def __post_init__(self) -> None:
        if not self.supported_languages:
            raise ValueError("Danh sách ngôn ngữ PII không được rỗng.")
        if self.default_language not in self.supported_languages:
            raise ValueError("Ngôn ngữ PII mặc định chưa được khai báo hỗ trợ.")
        if not 0 <= self.score_threshold <= 1:
            raise ValueError("Ngưỡng nhận diện PII phải nằm trong khoảng 0 đến 1.")

    def resolve(self, language: str | None) -> str:
        """Chuẩn hóa và kiểm tra language của một lần phân tích.

        Args:
            language: Mã ngôn ngữ hoặc `None` để dùng cấu hình mặc định.

        Returns:
            Mã ngôn ngữ hợp lệ.

        Raises:
            ValueError: Khi language chưa được cấu hình hỗ trợ.
        """
        resolved = language or self.default_language
        if resolved not in self.supported_languages:
            raise ValueError(f"Ngôn ngữ PII chưa được hỗ trợ: {resolved}")
        return resolved
