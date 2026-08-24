"""Application outputs độc lập HTTP cho health checks."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class DatabaseHealthOutput:
    status: Literal["healthy", "unhealthy"]
    latency_ms: float


@dataclass(frozen=True, slots=True)
class LlmHealthOutput:
    status: Literal["configured", "unconfigured"]
    provider: str
    model: str


@dataclass(frozen=True, slots=True)
class HealthOutput:
    status: Literal["ok", "degraded"]
    env: str
    version: str
    database: DatabaseHealthOutput
    llm: LlmHealthOutput

