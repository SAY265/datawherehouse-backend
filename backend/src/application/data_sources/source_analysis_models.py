"""Application models cho source analysis và column classification."""

from dataclasses import dataclass

from src.domain.data_source.column_profile import ColumnProfile
from src.domain.data_source.enums import ColumnDataType
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ProfiledTableSource:
    """Profile một table độc lập định dạng file cụ thể."""

    table_name: str
    columns: tuple[ColumnProfile, ...]
    declared_columns: tuple[ColumnMetadata, ...] | None = None


@dataclass(frozen=True, slots=True)
class ProfiledSource:
    """Tập table đã profile thuộc cùng một Data Source."""

    tables: tuple[ProfiledTableSource, ...]


@dataclass(frozen=True, slots=True)
class SourceFileAnalysisInput:
    """File source cần được phân tích trong một workflow action."""

    source_id: EntityID
    filename: str
    content: bytes


@dataclass(frozen=True, slots=True)
class ColumnClassificationInput:
    """Metadata giới hạn gửi cho structured LLM classifier."""

    reference: str
    profile: ColumnProfile
    candidate_type: ColumnDataType


@dataclass(frozen=True, slots=True)
class ColumnClassificationOutput:
    """Kết quả classifier đã giới hạn enum."""

    reference: str
    data_type: ColumnDataType
    confidence: float


@dataclass(frozen=True, slots=True)
class AnalyzedSourceSchema:
    """Schema cuối cùng gắn đúng Data Source."""

    source_id: EntityID
    schema_metadata: SchemaMetadata
