"""Process-scoped resources cho Data Model và Agent composition."""

from functools import lru_cache

from config import get_settings
from src.infrastructure.security.pii.factory import build_pii_masking_service
from src.infrastructure.security.pii.language_configuration import PiiLanguageConfiguration
from src.infrastructure.security.pii_guard import PiiGuard
from src.infrastructure.validation.dbml_validation_engine import DbmlValidationEngine


@lru_cache
def get_pii_guard() -> PiiGuard:
    """Cấp phát PII Guard dùng chung cho mọi Agent invocation."""
    settings = get_settings()
    configuration = PiiLanguageConfiguration(
        settings.pii_supported_languages_list,
        settings.pii_default_language,
        settings.pii_score_threshold,
    )
    service = build_pii_masking_service(configuration)
    return PiiGuard(settings.pii_masking_enabled, service, settings.pii_default_language)


@lru_cache
def get_validation_engine() -> DbmlValidationEngine:
    """Cấp phát deterministic ValidationEngine dùng chung."""
    return DbmlValidationEngine()
