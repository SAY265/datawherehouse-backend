"""Safe scalar conversion for SQL metadata and preview values."""

from sqlglot import exp
from src.domain.shared.types import JsonScalar


def sql_scalar(node: exp.Expression) -> JsonScalar:
    """Convert literals only; retain other expressions as inert SQL text."""
    if isinstance(node, exp.Null):
        return None
    if isinstance(node, exp.Boolean):
        return bool(node.this)
    if isinstance(node, exp.Literal):
        value = node.to_py()
        return value if isinstance(value, (str, int, float, bool)) else str(value)
    return node.sql()
