"""Composition root cho Health service."""

from config import get_settings
from src.application.health.health_service import HealthService
from src.application.health.i_health_service import IHealthService
from src.infrastructure.database.config import get_async_db_engine
from src.infrastructure.health.sqlalchemy_health_probe import SqlAlchemyHealthProbe


def get_health_service() -> IHealthService:
    settings = get_settings()
    api_key = settings.llm_api_key or settings.openai_api_key or settings.google_api_key
    return HealthService(
        SqlAlchemyHealthProbe(get_async_db_engine()),
        settings.app_env,
        "1.0.0",
        settings.llm_provider,
        settings.model_name,
        bool(api_key.strip()),
    )

