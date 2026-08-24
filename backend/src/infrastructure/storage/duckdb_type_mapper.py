"""Nguồn sự thật ánh xạ physical type DuckDB sang Domain type."""

from typing import Final

INTEGER_TYPES: Final = frozenset(
    {
        "TINYINT",
        "SMALLINT",
        "INTEGER",
        "BIGINT",
        "HUGEINT",
        "UTINYINT",
        "USMALLINT",
        "UINTEGER",
        "UBIGINT",
        "UHUGEINT",
    }
)
NUMBER_TYPES: Final = frozenset({"FLOAT", "DOUBLE", "REAL"})


def map_duckdb_type(type_name: str) -> str:
    """Ánh xạ tên kiểu DuckDB sang physical type ổn định của Domain."""
    normalized = type_name.strip().upper()
    base_type = normalized.partition("(")[0]
    if base_type in INTEGER_TYPES:
        return "INTEGER"
    if base_type in NUMBER_TYPES:
        return "NUMBER"
    if base_type == "DECIMAL":
        return "DECIMAL"
    if normalized.startswith("TIMESTAMP"):
        return "DATETIME"
    if normalized.startswith("TIME"):
        return "TIME"
    if base_type in {"DATE", "BOOLEAN"}:
        return base_type
    return "TEXT"
