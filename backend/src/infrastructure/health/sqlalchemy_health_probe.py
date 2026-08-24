"""Database health probe có timeout và không làm lộ exception."""

import asyncio
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from src.application.health.i_health_service import IDatabaseHealthProbe
from src.application.health.models import DatabaseHealthOutput
from typing_extensions import override


class SqlAlchemyHealthProbe(IDatabaseHealthProbe):
    """Ping SQLAlchemy asynchronously within a bounded readiness timeout."""

    def __init__(self, engine: AsyncEngine, timeout_seconds: float = 2.0) -> None:
        self._engine = engine
        self._timeout_seconds = timeout_seconds

    @override
    async def check(self) -> DatabaseHealthOutput:
        """Return sanitized health and latency without exposing database exceptions."""
        started = time.perf_counter()
        try:
            await asyncio.wait_for(self._ping(), timeout=self._timeout_seconds)
        except Exception:
            return DatabaseHealthOutput("unhealthy", _elapsed_ms(started))
        return DatabaseHealthOutput("healthy", _elapsed_ms(started))

    async def _ping(self) -> None:
        async with self._engine.connect() as connection:
            await connection.execute(text("SELECT 1"))


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 2)
