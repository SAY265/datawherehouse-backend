"""Map declared SQL types onto the source-analysis logical type system."""

from src.domain.data_source.enums import ColumnDataType


def logical_type(type_name: str) -> ColumnDataType:
    """Return a stable logical type without depending on a SQL dialect runtime."""
    normalized = type_name.upper()
    if "BOOL" in normalized:
        return ColumnDataType.BOOLEAN
    if "INT" in normalized:
        return ColumnDataType.INTEGER
    if "DECIMAL" in normalized or "NUMERIC" in normalized:
        return ColumnDataType.DECIMAL
    if any(item in normalized for item in ("FLOAT", "DOUBLE", "REAL")):
        return ColumnDataType.NUMBER
    if "TIMESTAMP" in normalized or "DATETIME" in normalized:
        return ColumnDataType.DATETIME
    if normalized.startswith("DATE"):
        return ColumnDataType.DATE
    if normalized.startswith("TIME"):
        return ColumnDataType.TIME
    return ColumnDataType.TEXT
