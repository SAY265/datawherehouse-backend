"""Parse SQL uploads through SQLGlot AST without executing statements."""

from sqlglot import parse
from sqlglot.errors import ParseError
from src.domain.data_source.enums import DataSourceType
from src.infrastructure.storage.sql_insert_parser import parse_insert_rows
from src.infrastructure.storage.sql_schema_parser import parse_create_tables
from src.infrastructure.storage.tabular_source_models import ParsedSource, ParsedTable


def parse_sql(content: bytes) -> ParsedSource:
    """Read CREATE TABLE metadata and literal INSERT VALUES previews."""
    try:
        statements = parse(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, ParseError) as exc:
        raise ValueError("SQL không hợp lệ hoặc không dùng UTF-8.") from exc
    tables = parse_create_tables(statements)
    rows_by_table = parse_insert_rows(statements, tables)
    parsed = tuple(
        ParsedTable(name, tuple(item.name for item in columns), tuple(rows_by_table[name]), columns)
        for name, columns in tables.items()
    )
    return ParsedSource(DataSourceType.SQL, parsed)
