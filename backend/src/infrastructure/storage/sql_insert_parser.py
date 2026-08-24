"""Extract inert INSERT VALUES rows for SQL source previews."""

from sqlglot import exp
from src.domain.data_source.value_objects import ColumnMetadata
from src.domain.shared.types import JsonScalar
from src.infrastructure.storage.sql_expression_values import sql_scalar


def parse_insert_rows(
    statements: list[exp.Expression | None],
    tables: dict[str, tuple[ColumnMetadata, ...]],
) -> dict[str, list[tuple[JsonScalar, ...]]]:
    """Collect only VALUES belonging to a declared uploaded table."""
    result = {name: [] for name in tables}
    for statement in statements:
        if not isinstance(statement, exp.Insert) or not isinstance(statement.expression, exp.Values):
            continue
        target, insert_columns = _insert_target(statement.this)
        if target not in tables:
            continue
        declared = tuple(item.name for item in tables[target])
        for row in statement.expression.expressions:
            values = tuple(sql_scalar(item) for item in row.expressions)
            result[target].append(_align_row(declared, insert_columns, values))
    return result


def _insert_target(node: exp.Expression) -> tuple[str, tuple[str, ...]]:
    if isinstance(node, exp.Schema) and isinstance(node.this, exp.Table):
        return node.this.sql(), tuple(item.name for item in node.expressions)
    if isinstance(node, exp.Table):
        return node.sql(), ()
    return "", ()


def _align_row(
    declared: tuple[str, ...],
    insert_columns: tuple[str, ...],
    values: tuple[JsonScalar, ...],
) -> tuple[JsonScalar, ...]:
    if not insert_columns:
        return (values + (None,) * len(declared))[: len(declared)]
    mapping = dict(zip(insert_columns, values, strict=False))
    return tuple(mapping.get(name) for name in declared)
