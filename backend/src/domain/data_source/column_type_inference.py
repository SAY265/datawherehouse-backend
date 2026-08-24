"""Rule-based logical type inference không phụ thuộc DuckDB hoặc LLM."""

import re
import unicodedata
from typing import Final

from src.domain.data_source.column_profile import ColumnProfile, LogicalTypeDecision
from src.domain.data_source.enums import ColumnDataType

DATE_MATCH_THRESHOLD: Final = 0.95
MAX_CATEGORY_VALUES: Final = 20
IDENTIFIER_HINTS: Final = ("_id", "id_", "code", "uuid", "identifier", "ma_", "so_ho_so")
FREE_TEXT_HINTS: Final = ("note", "notes", "description", "comment", "ghi_chu", "mo_ta")
CATEGORY_HINTS: Final = ("category", "gender", "sex", "status", "state", "type", "tier", "level", "gioi_tinh")


def infer_logical_type(profile: ColumnProfile) -> LogicalTypeDecision:
    """Suy luận candidate type và confidence từ profile thuần."""
    name = _normalize_name(profile.name)
    if profile.datetime_match_ratio >= DATE_MATCH_THRESHOLD:
        return LogicalTypeDecision(ColumnDataType.DATETIME, 0.98)
    if profile.date_match_ratio >= DATE_MATCH_THRESHOLD:
        return LogicalTypeDecision(ColumnDataType.DATE, 0.98)
    if is_identifier_like(profile):
        return LogicalTypeDecision(ColumnDataType.TEXT, 0.97)
    if _has_hint(name, FREE_TEXT_HINTS):
        return LogicalTypeDecision(ColumnDataType.TEXT, 0.96)
    candidate = _physical_candidate(profile.physical_type)
    if candidate is not ColumnDataType.TEXT:
        return _numeric_or_scalar_decision(profile, candidate)
    return _text_decision(profile, name)


def _numeric_or_scalar_decision(
    profile: ColumnProfile,
    candidate: ColumnDataType,
) -> LogicalTypeDecision:
    if (
        candidate in {ColumnDataType.INTEGER, ColumnDataType.NUMBER, ColumnDataType.DECIMAL}
        and profile.is_fixed_length
        and profile.average_length >= 6
        and profile.distinct_ratio >= 0.9
    ):
        return LogicalTypeDecision(ColumnDataType.TEXT, 0.65)
    return LogicalTypeDecision(candidate, 0.94)


def _text_decision(profile: ColumnProfile, name: str) -> LogicalTypeDecision:
    is_bounded = 0 < profile.distinct_count <= MAX_CATEGORY_VALUES
    has_distribution_signal = (
        profile.total_rows > 0
        and profile.distinct_ratio <= 0.5
        and profile.average_length <= 64
        and profile.top_value_ratio > 0
    )
    if is_bounded and has_distribution_signal and _has_hint(name, CATEGORY_HINTS):
        return LogicalTypeDecision(ColumnDataType.CATEGORY, 0.94)
    return LogicalTypeDecision(ColumnDataType.TEXT, 0.65)


def is_identifier_like(profile: ColumnProfile) -> bool:
    """Nhận diện strong identifier signal dùng chung cho type và key candidate."""
    return profile.has_leading_zero or _has_hint(
        _normalize_name(profile.name),
        IDENTIFIER_HINTS,
    )


def _physical_candidate(type_name: str) -> ColumnDataType:
    normalized = type_name.upper()
    if "BOOL" in normalized:
        return ColumnDataType.BOOLEAN
    if "INT" in normalized:
        return ColumnDataType.INTEGER
    if "DECIMAL" in normalized or "NUMERIC" in normalized:
        return ColumnDataType.DECIMAL
    if any(item in normalized for item in ("DOUBLE", "FLOAT", "REAL")):
        return ColumnDataType.NUMBER
    if normalized == "TIME":
        return ColumnDataType.TIME
    return ColumnDataType.TEXT


def _normalize_name(name: str) -> str:
    ascii_name = "".join(
        character
        for character in unicodedata.normalize("NFKD", name.casefold())
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "_", ascii_name).strip("_")


def _has_hint(name: str, hints: tuple[str, ...]) -> bool:
    wrapped = f"_{name}_"
    return any(f"_{hint.strip('_')}_" in wrapped for hint in hints)
