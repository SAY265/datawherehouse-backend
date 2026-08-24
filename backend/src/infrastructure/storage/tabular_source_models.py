"""Các model nội bộ dùng chung cho parser source dạng bảng."""

from dataclasses import dataclass, field

from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.value_objects import ColumnMetadata
from src.domain.shared.types import JsonScalar


@dataclass(frozen=True, slots=True)
class ParsedTable:
    """Một table đã parse nhưng chưa chạy profiling."""

    name: str
    columns: tuple[str, ...]
    rows: tuple[tuple[JsonScalar, ...], ...] = field(default_factory=tuple)
    declared_columns: tuple[ColumnMetadata, ...] | None = None


@dataclass(frozen=True, slots=True)
class ParsedSource:
    """Kết quả parse đầy đủ của một file source."""

    source_type: DataSourceType
    tables: tuple[ParsedTable, ...]
