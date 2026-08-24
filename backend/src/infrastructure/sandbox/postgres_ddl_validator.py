"""Kiểm tra script PostgreSQL DDL bằng SQLGlot."""

import re

from sqlglot import exp, parse
from sqlglot.errors import ParseError

ALLOWED_DDL_EXPRESSIONS = (exp.Create, exp.Alter, exp.Drop, exp.Comment)
ALLOWED_DDL_KINDS = {"INDEX", "SEQUENCE", "TABLE", "VIEW"}
ALLOWED_COMMENT_KINDS = {"COLUMN", "TABLE", "VIEW"}
ENUM_VALUE = r"'(?:''|[^'])*'"
IDENTIFIER = r'(?:"(?:[^"]|"")*"|[A-Za-z_][A-Za-z0-9_]*)'
CREATE_ENUM_PATTERN = re.compile(
    rf"^CREATE\s+TYPE\s+(?:(?P<schema>{IDENTIFIER})\s*\.\s*)?{IDENTIFIER}"
    rf"\s+AS\s+ENUM\s*\(\s*{ENUM_VALUE}(?:\s*,\s*{ENUM_VALUE})*\s*\)$",
    re.IGNORECASE | re.DOTALL,
)


def split_ddl_statements(ddl_script: str, allowed_schema: str | None = None) -> list[str]:
    """Parse và xác thực từng statement DDL PostgreSQL."""
    try:
        expressions = parse(ddl_script, read="postgres")
    except ParseError as exc:
        raise ValueError(f"DDL không hợp lệ: {exc}") from exc
    return [_validate_expression(item, allowed_schema) for item in expressions if item]


def _validate_expression(expression: exp.Expression, allowed_schema: str | None) -> str:
    """Xác thực loại biểu thức và namespace rồi render chuẩn hóa."""
    if isinstance(expression, exp.Command):
        statement = expression.sql(dialect="postgres").strip()
        _validate_enum_command(statement, allowed_schema)
        return statement
    if not isinstance(expression, ALLOWED_DDL_EXPRESSIONS):
        raise ValueError(
            f"Chỉ cho phép câu lệnh DDL; nhận được {type(expression).__name__}."
        )
    _validate_kind(expression)
    _validate_scope(expression, allowed_schema)
    return expression.sql(dialect="postgres")


def _validate_kind(expression: exp.Expression) -> None:
    """Chỉ cho phép các đối tượng DDL an toàn."""
    kind = str(expression.args.get("kind") or "").upper()
    allowed = ALLOWED_COMMENT_KINDS if isinstance(expression, exp.Comment) else ALLOWED_DDL_KINDS
    if kind not in allowed:
        prefix = "COMMENT ON" if isinstance(expression, exp.Comment) else "DDL trên đối tượng"
        raise ValueError(f"{prefix} {kind or 'UNKNOWN'} không được phép trong Sandbox.")


def _validate_scope(expression: exp.Expression, allowed_schema: str | None) -> None:
    """Cấm catalog và tham chiếu ra ngoài schema sandbox."""
    if not allowed_schema:
        return
    for relation in expression.find_all(exp.Table):
        _validate_namespace(relation.catalog, relation.db, allowed_schema)
    for column in expression.find_all(exp.Column):
        _validate_namespace(column.catalog, column.db, allowed_schema)


def _validate_namespace(catalog: str, schema: str, allowed_schema: str) -> None:
    """Xác thực namespace của table hoặc column."""
    if catalog:
        raise ValueError("DDL không được tham chiếu database/catalog khác.")
    if schema and schema.casefold() != allowed_schema.casefold():
        raise ValueError(f"DDL chỉ được thao tác trong schema '{allowed_schema}'.")


def _validate_enum_command(statement: str, allowed_schema: str | None) -> None:
    """Cho phép duy nhất CREATE TYPE AS ENUM mà SQLGlot trả về Command."""
    match = CREATE_ENUM_PATTERN.fullmatch(statement)
    if match is None:
        raise ValueError("Câu lệnh DDL này chưa được hỗ trợ trong Sandbox.")
    schema = match.group("schema")
    normalized = _unquote(schema) if schema else None
    if normalized and allowed_schema and normalized.casefold() != allowed_schema.casefold():
        raise ValueError(f"DDL chỉ được thao tác trong schema '{allowed_schema}'.")


def _unquote(identifier: str) -> str:
    """Bỏ quote an toàn khỏi PostgreSQL identifier."""
    if identifier.startswith('"') and identifier.endswith('"'):
        return identifier[1:-1].replace('""', '"')
    return identifier
