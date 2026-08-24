"""Đọc CSV bằng DuckDB sniffer và chỉ trả primitive nội bộ."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import duckdb
from src.domain.shared.types import JsonValue
from src.infrastructure.storage.duckdb_scalar_mapper import to_json_scalar

CSV_TABLE_NAME: Final = "parsed_csv"
MAX_PREVIEW_ROWS: Final = 5
AUTO_TYPE_CANDIDATES: Final = (
    "BOOLEAN",
    "BIGINT",
    "DECIMAL",
    "DOUBLE",
    "TIME",
    "DATE",
    "TIMESTAMP",
)


@dataclass(frozen=True, slots=True)
class DuckDbCsvColumn:
    """Tên và physical type đã được DuckDB suy luận."""

    name: str
    type_name: str


@dataclass(frozen=True, slots=True)
class DuckDbCsvSnapshot:
    """Thông tin CSV tối thiểu được đưa sang profiler và output mapper."""

    columns: tuple[DuckDbCsvColumn, ...]
    total_rows: int
    preview_rows: tuple[dict[str, JsonValue], ...]


def read_csv_snapshot(
    connection: duckdb.DuckDBPyConnection,
    path: Path,
    delimiter: str | None = None,
) -> DuckDbCsvSnapshot:
    """Sniff CSV, materialize table và lấy preview giới hạn."""
    options: dict[str, object] = {"auto_type_candidates": list(AUTO_TYPE_CANDIDATES)}
    if delimiter is not None:
        options["delimiter"] = delimiter
    relation = connection.read_csv(str(path), **options)
    columns = tuple(
        DuckDbCsvColumn(name, str(type_name))
        for name, type_name in zip(relation.columns, relation.types, strict=True)
    )
    relation.create(CSV_TABLE_NAME)
    total_rows = int(connection.execute(f"SELECT count(*) FROM {CSV_TABLE_NAME}").fetchone()[0])
    return DuckDbCsvSnapshot(columns, total_rows, _fetch_preview(connection, columns))


def _fetch_preview(
    connection: duckdb.DuckDBPyConnection,
    columns: tuple[DuckDbCsvColumn, ...],
) -> tuple[dict[str, JsonValue], ...]:
    """Lấy đúng các dòng đầu file mà không tải toàn bộ dữ liệu vào Python."""
    if not columns:
        return ()
    selected = ", ".join(quote_identifier(column.name) for column in columns)
    rows = connection.execute(
        f"SELECT {selected} FROM {CSV_TABLE_NAME} ORDER BY rowid LIMIT ?",
        [MAX_PREVIEW_ROWS],
    ).fetchall()
    return tuple(
        {
            column.name: to_json_scalar(value)
            for column, value in zip(columns, row, strict=True)
        }
        for row in rows
    )


def quote_identifier(identifier: str) -> str:
    """Quote identifier do CSV cung cấp để dùng an toàn trong SQL nội bộ."""
    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'
