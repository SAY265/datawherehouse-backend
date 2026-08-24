"""Dispatch parser cho các source không phải delimited text."""

from pathlib import Path

from src.infrastructure.storage.excel_source_parser import parse_excel
from src.infrastructure.storage.markdown_source_parser import parse_markdown
from src.infrastructure.storage.sql_source_parser import parse_sql
from src.infrastructure.storage.tabular_source_models import ParsedSource


def parse_structured_source(content: bytes, filename: str) -> ParsedSource:
    """Chọn parser theo extension đã được upload policy cho phép."""
    suffix = Path(filename).suffix.lower()
    if suffix in {".xls", ".xlsx"}:
        return parse_excel(content, filename)
    if suffix in {".md", ".markdown"}:
        try:
            return parse_markdown(content)
        except UnicodeDecodeError as exc:
            raise ValueError("Markdown không dùng UTF-8.") from exc
    if suffix == ".sql":
        return parse_sql(content)
    raise ValueError(f"Không có parser cho extension {suffix}.")
