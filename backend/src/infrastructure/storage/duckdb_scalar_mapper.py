"""Chuyển scalar DuckDB thành primitive JSON an toàn."""

from datetime import date, datetime, time
from decimal import Decimal

from src.domain.shared.types import JsonScalar


def to_json_scalar(value: object) -> JsonScalar:
    """Chuyển giá trị từ DuckDB boundary sang JSON scalar."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return str(value)
