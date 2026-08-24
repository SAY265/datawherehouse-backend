"""Outbound ports cho CSV profiling và logical type classification."""

from typing import Protocol

from src.application.data_sources.output import PreviewOutput
from src.application.data_sources.source_analysis_models import (
    ColumnClassificationInput,
    ColumnClassificationOutput,
    ProfiledSource,
)
from src.domain.data_source.enums import DataSourceType


class ISourceFileInspector(Protocol):
    """Port validate, preview và profile source độc lập định dạng."""

    def validate(self, file_bytes: bytes, filename: str) -> None: ...

    def profile(self, file_bytes: bytes, filename: str) -> ProfiledSource: ...

    def preview(
        self,
        file_bytes: bytes,
        filename: str,
        table_name: str | None,
    ) -> PreviewOutput: ...

    def source_type(self, filename: str) -> DataSourceType:
        """Ánh xạ extension đã hỗ trợ sang loại source."""
        ...


class IColumnTypeClassifier(Protocol):
    """Port structured LLM cho các cột rule engine chưa chắc chắn."""

    async def classify(
        self,
        columns: tuple[ColumnClassificationInput, ...],
    ) -> tuple[ColumnClassificationOutput, ...]:
        """Phân loại một batch metadata cột giới hạn."""
        ...
