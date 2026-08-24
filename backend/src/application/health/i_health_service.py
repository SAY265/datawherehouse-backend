"""Interface duy nhất của application module Health."""

from abc import ABC, abstractmethod
from typing import Protocol

from src.application.health.models import DatabaseHealthOutput, HealthOutput


class IDatabaseHealthProbe(Protocol):
    async def check(self) -> DatabaseHealthOutput: ...


class IHealthService(ABC):
    @abstractmethod
    async def check(self) -> HealthOutput:
        """Kiểm tra dependency mà không làm lộ lỗi kỹ thuật."""
        raise NotImplementedError

