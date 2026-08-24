"""Port for analyzing a Data Model with a language model."""

from abc import ABC, abstractmethod

from src.application.data_models.output import DataModelInsightOutput


class IDataModelInsightAnalyzer(ABC):
    """Async contract for the T-028 insight analyzer."""

    @abstractmethod
    async def analyze(self, dbml: str) -> list[DataModelInsightOutput]:
        """Analyze DBML and return grounded insights."""
        raise NotImplementedError
