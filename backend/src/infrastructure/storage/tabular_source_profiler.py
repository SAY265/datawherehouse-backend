"""Profiler thuần cho các parser đã materialize table trong bộ nhớ."""

from datetime import datetime

from src.application.data_sources.source_analysis_models import (
    ProfiledSource,
    ProfiledTableSource,
)
from src.domain.data_source.column_profile import ColumnProfile
from src.domain.shared.types import JsonScalar
from src.infrastructure.storage.tabular_source_models import ParsedSource, ParsedTable

MAX_DISTINCT_VALUES = 20
MAX_SAMPLE_VALUES = 10
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")
DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
)


def profile_source(source: ParsedSource) -> ProfiledSource:
    """Tạo profile cho toàn bộ table đã parse."""
    return ProfiledSource(tuple(_profile_table(table) for table in source.tables))


def _profile_table(table: ParsedTable) -> ProfiledTableSource:
    columns = tuple(
        _profile_column(name, tuple(row[index] for row in table.rows))
        for index, name in enumerate(table.columns)
    )
    return ProfiledTableSource(table.name, columns, table.declared_columns)


def _profile_column(name: str, values: tuple[JsonScalar, ...]) -> ColumnProfile:
    present = tuple(value for value in values if value is not None and value != "")
    strings = tuple(str(value) for value in present)
    distinct = tuple(dict.fromkeys(strings))
    lengths = tuple(len(value) for value in strings)
    return ColumnProfile(
        name=name,
        physical_type=_physical_type(present),
        sample_values=distinct[:MAX_SAMPLE_VALUES],
        distinct_values=distinct[:MAX_DISTINCT_VALUES],
        null_count=len(values) - len(present),
        distinct_count=len(set(strings)),
        total_rows=len(values),
        average_length=sum(lengths) / len(lengths) if lengths else 0,
        is_fixed_length=bool(lengths) and min(lengths) == max(lengths),
        has_leading_zero=any(value.startswith("0") and value.isdigit() for value in strings),
        date_match_ratio=_match_ratio(strings, DATE_FORMATS),
        datetime_match_ratio=_match_ratio(strings, DATETIME_FORMATS),
        top_value_ratio=_top_ratio(strings),
    )


def _physical_type(values: tuple[JsonScalar, ...]) -> str:
    if values and all(isinstance(value, bool) for value in values):
        return "BOOLEAN"
    if values and all(isinstance(value, int) and not isinstance(value, bool) for value in values):
        return "BIGINT"
    if values and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
        return "DOUBLE"
    return "VARCHAR"


def _match_ratio(values: tuple[str, ...], formats: tuple[str, ...]) -> float:
    if not values:
        return 0
    matched = sum(any(_matches(value, pattern) for pattern in formats) for value in values)
    return matched / len(values)


def _matches(value: str, pattern: str) -> bool:
    try:
        datetime.strptime(value, pattern)
    except ValueError:
        return False
    return True


def _top_ratio(values: tuple[str, ...]) -> float:
    if not values:
        return 0
    frequencies = {value: values.count(value) for value in set(values)}
    return max(frequencies.values()) / len(values)
