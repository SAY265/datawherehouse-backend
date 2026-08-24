"""Custom recognizer có validation và context scoring độc lập NLP engine."""

from collections.abc import Callable
from dataclasses import dataclass

import regex
from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

PatternValidator = Callable[[str], bool]


@dataclass(frozen=True, slots=True)
class ContextPatternConfiguration:
    """Cấu hình cho một recognizer pattern có context."""

    name: str
    entity_type: str
    language: str
    pattern: str
    context_words: tuple[str, ...]
    base_score: float
    contextual_score: float
    context_window: int = 32
    validator: PatternValidator | None = None


class ContextPatternRecognizer(EntityRecognizer):
    """Recognizer chỉ nâng confidence khi pattern có ngữ cảnh đáng tin cậy."""

    def __init__(self, configuration: ContextPatternConfiguration) -> None:
        """Khởi tạo plugin từ một value object cấu hình."""
        super().__init__(
            supported_entities=[configuration.entity_type],
            name=configuration.name,
            supported_language=configuration.language,
            context=list(configuration.context_words),
        )
        self._configuration = configuration
        self._pattern = regex.compile(configuration.pattern, regex.IGNORECASE)

    def analyze(
        self,
        text: str,
        entities: list[str],
        nlp_artifacts: NlpArtifacts | None = None,
    ) -> list[RecognizerResult]:
        """Tìm pattern, validate rồi chấm điểm theo vùng context lân cận."""
        del nlp_artifacts
        if self._configuration.entity_type not in entities:
            return []
        results: list[RecognizerResult] = []
        for match in self._pattern.finditer(text):
            value = match.group("value")
            if not self._is_valid(value):
                continue
            start, end = match.span("value")
            results.append(self._build_result(text, start, end))
        return results

    def _is_valid(self, value: str) -> bool:
        """Chạy validation riêng của recognizer nếu được cấu hình."""
        validator = self._configuration.validator
        return validator(value) if validator else True

    def _build_result(self, text: str, start: int, end: int) -> RecognizerResult:
        """Tạo kết quả với confidence đã xét context."""
        configuration = self._configuration
        context_start = max(0, start - configuration.context_window)
        context_end = min(len(text), end + configuration.context_window)
        context = text[context_start:context_end].casefold()
        has_context = any(word.casefold() in context for word in configuration.context_words)
        score = configuration.contextual_score if has_context else configuration.base_score
        return RecognizerResult(configuration.entity_type, start, end, score)
