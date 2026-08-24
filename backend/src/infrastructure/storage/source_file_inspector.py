"""Adapter thống nhất validate, profile và preview mọi source được hỗ trợ."""

import csv
from io import StringIO
from pathlib import Path
from typing import NoReturn

from src.application.data_sources.output import PreviewOutput
from src.application.data_sources.source_analysis_models import ProfiledSource
from src.application.data_sources.source_analysis_ports import ISourceFileInspector
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.enums import DataSourceType
from src.infrastructure.storage.duckdb_csv_file_reader import DuckDbCsvFileReader
from src.infrastructure.storage.duckdb_csv_profiler import DuckDbCsvProfiler
from src.infrastructure.storage.structured_source_parser import parse_structured_source
from src.infrastructure.storage.structured_source_preview import structured_preview
from src.infrastructure.storage.tabular_source_models import ParsedTable
from src.infrastructure.storage.tabular_source_profiler import profile_source
from typing_extensions import override

DELIMITED_TYPES = {".csv": DataSourceType.CSV, ".tsv": DataSourceType.TSV}
STRUCTURED_TYPES = {
    ".xls": DataSourceType.EXCEL,
    ".xlsx": DataSourceType.EXCEL,
    ".md": DataSourceType.MARKDOWN,
    ".markdown": DataSourceType.MARKDOWN,
    ".sql": DataSourceType.SQL,
}


class SourceFileInspector(ISourceFileInspector):
    """Điều phối adapter cụ thể và dịch lỗi parser về error contract chung."""

    def __init__(self) -> None:
        self._delimited_reader = DuckDbCsvFileReader()
        self._delimited_profiler = DuckDbCsvProfiler()

    @override
    def validate(self, file_bytes: bytes, filename: str) -> None:
        if not file_bytes:
            _raise(filename, "File rỗng.")
        try:
            if _suffix(filename) in DELIMITED_TYPES:
                _validate_delimited_headers(file_bytes, filename)
                self._delimited_reader.validate(file_bytes, filename)
                return
            source = parse_structured_source(file_bytes, filename)
            _validate_tables(source.tables)
        except InfrastructureException:
            raise
        except (OSError, ValueError) as exc:
            _raise(filename, str(exc), exc)

    @override
    def profile(self, file_bytes: bytes, filename: str) -> ProfiledSource:
        try:
            if _suffix(filename) in DELIMITED_TYPES:
                table = self._delimited_profiler.profile(file_bytes, filename)
                return ProfiledSource((table,))
            source = parse_structured_source(file_bytes, filename)
            _validate_tables(source.tables)
            return profile_source(source)
        except InfrastructureException:
            raise
        except (OSError, ValueError) as exc:
            _raise(filename, str(exc), exc)

    @override
    def preview(
        self, file_bytes: bytes, filename: str, table_name: str | None
    ) -> PreviewOutput:
        try:
            if _suffix(filename) in DELIMITED_TYPES:
                return self._delimited_reader.read(file_bytes, filename)
            source = parse_structured_source(file_bytes, filename)
            _validate_tables(source.tables)
            return structured_preview(source, table_name)
        except InfrastructureException:
            raise
        except (OSError, ValueError) as exc:
            _raise(filename, str(exc), exc)

    @override
    def source_type(self, filename: str) -> DataSourceType:
        suffix = _suffix(filename)
        source_type = DELIMITED_TYPES.get(suffix) or STRUCTURED_TYPES.get(suffix)
        if source_type is None:
            _raise(filename, "Extension không được hỗ trợ.")
        return source_type


def _suffix(filename: str) -> str:
    return Path(filename).suffix.lower()


def _raise(filename: str, reason: str, cause: Exception | None = None) -> NoReturn:
    error = InfrastructureException(
        ErrorCode.FILE_PARSING_ERROR,
        f"Không thể đọc file {filename}: {reason}",
    )
    raise error from cause


def _validate_tables(tables: tuple[ParsedTable, ...]) -> None:
    if not tables:
        raise ValueError("Không tìm thấy table hợp lệ.")
    for table in tables:
        if not table.columns or any(not name.strip() for name in table.columns):
            raise ValueError(f"Table {table.name} có header rỗng.")
        normalized = [name.casefold() for name in table.columns]
        if len(normalized) != len(set(normalized)):
            raise ValueError(f"Table {table.name} có header trùng.")


def _validate_delimited_headers(content: bytes, filename: str) -> None:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Delimited source không dùng UTF-8.") from exc
    delimiter = "\t" if _suffix(filename) == ".tsv" else ","
    headers = next(csv.reader(StringIO(text), delimiter=delimiter), [])
    normalized = [header.strip().casefold() for header in headers]
    if not normalized or any(not header for header in normalized):
        raise ValueError("Delimited source có header rỗng.")
    if len(normalized) != len(set(normalized)):
        raise ValueError("Delimited source có header trùng.")
