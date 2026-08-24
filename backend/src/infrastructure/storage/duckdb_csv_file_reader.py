"""Kiểm tra và đọc preview CSV nhẹ bằng DuckDB."""

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypeVar

import duckdb
from src.application.data_sources.output import PreviewOutput
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.storage.duckdb_csv_reader import read_csv_snapshot

ResultT = TypeVar("ResultT")


class DuckDbCsvFileReader:
    """Adapter DuckDB cho validation upload và preview không profiling."""

    def validate(self, file_bytes: bytes, filename: str) -> None:
        """Xác nhận CSV có nội dung, header và được DuckDB đọc thành công."""
        if not file_bytes.removeprefix(b"\xef\xbb\xbf").strip():
            _raise_file_error(filename)
        self._run(file_bytes, filename, _validate_path)

    def read(self, file_bytes: bytes, filename: str) -> PreviewOutput:
        """Đọc preview và chuyển scalar sang chuỗi cho HTTP output."""
        preview = self._run(file_bytes, filename, _read_preview)
        table_name = Path(filename).stem or "Table1"
        return PreviewOutput(
            table_name,
            (table_name,),
            preview.rows,
            preview.total_rows,
        )

    def _run(
        self,
        file_bytes: bytes,
        filename: str,
        operation: Callable[[duckdb.DuckDBPyConnection, Path], ResultT],
    ) -> ResultT:
        """Chạy operation DuckDB với file tạm và dịch lỗi hạ tầng."""
        try:
            with TemporaryDirectory(prefix="p102_csv_read_") as directory:
                path = Path(directory) / f"source{Path(filename).suffix.lower()}"
                path.write_bytes(file_bytes)
                with duckdb.connect() as connection:
                    return operation(connection, path)
        except (duckdb.Error, OSError) as exc:
            raise InfrastructureException(
                ErrorCode.FILE_PARSING_ERROR,
                f"Không thể đọc tệp CSV: {filename}",
            ) from exc


def _validate_path(connection: duckdb.DuckDBPyConnection, path: Path) -> None:
    relation = connection.read_csv(str(path), **_read_options(path))
    if not relation.columns:
        raise duckdb.InvalidInputException("CSV không có header.")
    relation.limit(0).fetchall()


def _read_preview(
    connection: duckdb.DuckDBPyConnection,
    path: Path,
) -> PreviewOutput:
    snapshot = read_csv_snapshot(connection, path, _delimiter(path))
    rows = tuple(
        {key: None if value is None else str(value) for key, value in row.items()} for row in snapshot.preview_rows
    )
    table_name = path.stem or "Table1"
    return PreviewOutput(table_name, (table_name,), rows, snapshot.total_rows)


def _read_options(path: Path) -> dict[str, str]:
    delimiter = _delimiter(path)
    return {"delimiter": delimiter} if delimiter is not None else {}


def _delimiter(path: Path) -> str | None:
    return "\t" if path.suffix.lower() == ".tsv" else None


def _raise_file_error(filename: str) -> None:
    raise InfrastructureException(
        ErrorCode.FILE_PARSING_ERROR,
        f"Tệp CSV rỗng hoặc không có header: {filename}",
    )
