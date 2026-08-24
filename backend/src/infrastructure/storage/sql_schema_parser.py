"""Extract table, column, type, and constraint metadata from SQLGlot AST."""

from dataclasses import replace

from sqlglot import exp
from src.domain.data_source.constraints import (
    CheckConstraint,
    ColumnConstraint,
    DefaultConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from src.domain.data_source.value_objects import ColumnMetadata
from src.infrastructure.storage.sql_expression_values import sql_scalar
from src.infrastructure.storage.sql_type_mapping import logical_type


def parse_create_tables(
    statements: list[exp.Expression | None],
) -> dict[str, tuple[ColumnMetadata, ...]]:
    """Build declared table schemas while ignoring non-CREATE statements."""
    tables: dict[str, tuple[ColumnMetadata, ...]] = {}
    for statement in statements:
        if not isinstance(statement, exp.Create) or str(statement.args.get("kind")).upper() != "TABLE":
            continue
        schema = statement.this
        if not isinstance(schema, exp.Schema) or not isinstance(schema.this, exp.Table):
            continue
        columns = [_column(item) for item in schema.expressions if isinstance(item, exp.ColumnDef)]
        tables[schema.this.sql()] = tuple(_apply_table_constraints(columns, schema.expressions))
    return tables


def _column(node: exp.ColumnDef) -> ColumnMetadata:
    constraints = []
    primary_key = False
    nullable = True
    for wrapper in node.args.get("constraints") or []:
        kind = wrapper.args.get("kind")
        primary_key = primary_key or isinstance(kind, exp.PrimaryKeyColumnConstraint)
        nullable = nullable and not isinstance(kind, exp.NotNullColumnConstraint)
        constraint = _column_constraint(kind)
        if constraint is not None:
            constraints.append(constraint)
    type_name = node.args["kind"].sql() if node.args.get("kind") else "TEXT"
    return ColumnMetadata(
        name=node.this.name,
        data_type=logical_type(type_name),
        primary_key=primary_key,
        nullable=nullable and not primary_key,
        constraints=tuple(constraints),
    )


def _column_constraint(node: exp.Expression | None) -> ColumnConstraint | None:
    if isinstance(node, exp.UniqueColumnConstraint):
        return UniqueConstraint()
    if isinstance(node, exp.Reference):
        table, column = _reference(node)
        return ForeignKeyConstraint(table, column)
    if isinstance(node, exp.CheckColumnConstraint):
        return CheckConstraint(node.this.sql())
    if isinstance(node, exp.DefaultColumnConstraint):
        return DefaultConstraint(sql_scalar(node.this))
    return None


def _apply_table_constraints(
    columns: list[ColumnMetadata],
    expressions: list[exp.Expression],
) -> list[ColumnMetadata]:
    by_name = {column.name: index for index, column in enumerate(columns)}
    for item in expressions:
        if isinstance(item, exp.PrimaryKey):
            for identifier in item.expressions:
                _mark_primary(columns, by_name, identifier.name)
        elif isinstance(item, exp.UniqueColumnConstraint):
            schema = item.this
            for identifier in schema.expressions if isinstance(schema, exp.Schema) else []:
                _append(columns, by_name, (identifier.name, UniqueConstraint()))
        elif isinstance(item, exp.ForeignKey):
            _apply_foreign_key(columns, by_name, item)
    return columns


def _apply_foreign_key(
    columns: list[ColumnMetadata],
    by_name: dict[str, int],
    item: exp.ForeignKey,
) -> None:
    reference = item.args.get("reference")
    if isinstance(reference, exp.Reference):
        table, target = _reference(reference)
        for identifier in item.expressions:
            _append(columns, by_name, (identifier.name, ForeignKeyConstraint(table, target)))


def _mark_primary(columns: list[ColumnMetadata], by_name: dict[str, int], name: str) -> None:
    if name in by_name:
        index = by_name[name]
        columns[index] = replace(columns[index], primary_key=True, nullable=False)


def _append(
    columns: list[ColumnMetadata],
    by_name: dict[str, int],
    update: tuple[str, ColumnConstraint],
) -> None:
    name, constraint = update
    if name in by_name:
        index = by_name[name]
        columns[index] = replace(columns[index], constraints=(*columns[index].constraints, constraint))


def _reference(node: exp.Reference) -> tuple[str, str]:
    schema = node.this
    if not isinstance(schema, exp.Schema) or not isinstance(schema.this, exp.Table):
        raise ValueError("FOREIGN KEY thiếu bảng hoặc cột tham chiếu.")
    column = schema.expressions[0].name if schema.expressions else "id"
    return schema.this.sql(), column
