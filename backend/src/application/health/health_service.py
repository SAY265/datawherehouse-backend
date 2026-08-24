"""Application service tổng hợp health dependency."""

from src.application.health.i_health_service import IDatabaseHealthProbe, IHealthService
from src.application.health.models import HealthOutput, LlmHealthOutput
from typing_extensions import override


class HealthService(IHealthService):
    def __init__(
        self,
        database: IDatabaseHealthProbe,
        env: str,
        version: str,
        llm_provider: str,
        llm_model: str,
        llm_configured: bool,
    ) -> None:
        self._database = database
        self._env = env
        self._version = version
        self._llm = LlmHealthOutput(
            "configured" if llm_configured else "unconfigured",
            llm_provider,
            llm_model,
        )

    @override
    async def check(self) -> HealthOutput:
        database = await self._database.check()
        status = "ok" if database.status == "healthy" else "degraded"
        return HealthOutput(status, self._env, self._version, database, self._llm)

