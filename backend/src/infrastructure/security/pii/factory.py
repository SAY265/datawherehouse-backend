"""Factory dựng một PII masking framework nhất quán."""

from collections.abc import Iterable
from functools import lru_cache

from presidio_analyzer import AnalyzerEngine, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpEngine, NoOpNlpEngine
from presidio_anonymizer import AnonymizerEngine
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.security.pii.language_configuration import (
    PiiLanguageConfiguration,
)
from src.infrastructure.security.pii.masking_service import PresidioPiiMaskingService
from src.infrastructure.security.pii.presidio_analyzer import PresidioPiiAnalyzer
from src.infrastructure.security.pii.presidio_anonymizer import PresidioPiiAnonymizer
from src.infrastructure.security.pii.recognizer_registry import PiiRecognizerRegistry
from src.infrastructure.security.pii.recognizers.recognizer_catalog import (
    build_catalog_recognizers,
)


def build_pii_masking_service(
    configuration: PiiLanguageConfiguration | None = None,
    nlp_engine: NlpEngine | None = None,
    extra_recognizers: Iterable[EntityRecognizer] = (),
) -> PresidioPiiMaskingService:
    """Dựng framework và integration point cho NLP/recognizer bên ngoài.

    Raises:
        InfrastructureException: Khi Presidio không thể khởi tạo.
    """
    selected = configuration or PiiLanguageConfiguration()
    recognizers = (*build_catalog_recognizers(selected.supported_languages), *extra_recognizers)
    try:
        analyzer, registry = _build_analyzer(selected, nlp_engine, recognizers)
    except (TypeError, ValueError) as exc:
        raise InfrastructureException(
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            message="Không thể khởi tạo PII masking framework.",
        ) from exc
    return PresidioPiiMaskingService(
        PresidioPiiAnalyzer(analyzer, selected, registry),
        PresidioPiiAnonymizer(AnonymizerEngine()),
    )


def _build_analyzer(
    configuration: PiiLanguageConfiguration,
    nlp_engine: NlpEngine | None,
    recognizers: Iterable[EntityRecognizer],
) -> tuple[AnalyzerEngine, PiiRecognizerRegistry]:
    """Dựng analyzer cùng registry có cùng language configuration."""
    engine = nlp_engine or _build_noop_nlp_engine(configuration)
    registry = PiiRecognizerRegistry(configuration, recognizers)
    registry.register_nlp_engine(engine)
    analyzer = AnalyzerEngine(
        registry=registry.presidio_registry,
        nlp_engine=engine,
        supported_languages=list(configuration.supported_languages),
        default_score_threshold=configuration.score_threshold,
    )
    return analyzer, registry


@lru_cache
def get_default_pii_masking_service() -> PresidioPiiMaskingService:
    """Trả framework mặc định đã cache cho toàn tiến trình."""
    return build_pii_masking_service()


def _build_noop_nlp_engine(configuration: PiiLanguageConfiguration) -> NoOpNlpEngine:
    """Dựng NLP engine nhẹ cho recognizer không phụ thuộc model NER."""
    models = [
        {"lang_code": language, "model_name": "noop"}
        for language in configuration.supported_languages
    ]
    return NoOpNlpEngine(models=models)
