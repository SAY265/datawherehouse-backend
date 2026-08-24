"""Parser XLS/XLSX chỉ đọc dữ liệu bằng python-calamine."""

from datetime import date, datetime, time
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from python_calamine import CalamineError, CalamineWorkbook
from src.domain.data_source.enums import DataSourceType
from src.domain.shared.types import JsonScalar
from src.infrastructure.storage.tabular_source_models import ParsedSource, ParsedTable

MAX_UNCOMPRESSED_XLSX_BYTES = 200 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100


def parse_excel(content: bytes, filename: str) -> ParsedSource:
    """Parse mỗi worksheet không rỗng thành một table."""
    if Path(filename).suffix.lower() == ".xlsx":
        _validate_xlsx_archive(content)
    try:
        workbook = CalamineWorkbook.from_filelike(BytesIO(content))
        tables = tuple(
            table
            for name in workbook.sheet_names
            if (table := _parse_sheet(workbook, name)) is not None
        )
        workbook.close()
    except (CalamineError, OSError, ValueError) as exc:
        raise ValueError("Workbook không hợp lệ hoặc không thể đọc.") from exc
    return ParsedSource(DataSourceType.EXCEL, tables)


def _parse_sheet(workbook: CalamineWorkbook, name: str) -> ParsedTable | None:
    values = workbook.get_sheet_by_name(name).to_python()
    rows = [row for row in values if any(value not in (None, "") for value in row)]
    if not rows:
        return None
    columns = tuple(str(value).strip() if value is not None else "" for value in rows[0])
    data = tuple(tuple(_scalar(value) for value in _pad(row, len(columns))) for row in rows[1:])
    return ParsedTable(name=name.strip() or "sheet", columns=columns, rows=data)


def _pad(row: list[object], width: int) -> list[object]:
    return (row + [None] * width)[:width]


def _scalar(value: object) -> JsonScalar:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    return str(value)


def _validate_xlsx_archive(content: bytes) -> None:
    try:
        with ZipFile(BytesIO(content)) as archive:
            compressed = max(sum(item.compress_size for item in archive.infolist()), 1)
            uncompressed = sum(item.file_size for item in archive.infolist())
    except BadZipFile as exc:
        raise ValueError("XLSX không phải ZIP Office hợp lệ.") from exc
    if uncompressed > MAX_UNCOMPRESSED_XLSX_BYTES:
        raise ValueError("XLSX vượt giới hạn dữ liệu giải nén.")
    if uncompressed / compressed > MAX_COMPRESSION_RATIO:
        raise ValueError("XLSX có tỷ lệ nén bất thường.")
