"""Parser các GFM table trong Markdown bằng markdown-it-py token AST."""

import re

from markdown_it import MarkdownIt
from markdown_it.token import Token
from src.domain.data_source.enums import DataSourceType
from src.infrastructure.storage.tabular_source_models import ParsedSource, ParsedTable


def parse_markdown(content: bytes) -> ParsedSource:
    """Parse table và dùng heading gần nhất làm tên ổn định."""
    text = content.decode("utf-8-sig")
    tokens = MarkdownIt("commonmark").enable("table").parse(text)
    tables: list[ParsedTable] = []
    heading: str | None = None
    index = 0
    while index < len(tokens):
        if tokens[index].type == "heading_open":
            heading = _next_inline(tokens, index)
        if tokens[index].type == "table_open":
            end = _find_close(tokens, index, "table_close")
            rows = _table_rows(tokens[index : end + 1])
            if rows:
                name = _unique_name(heading, len(tables), {item.name for item in tables})
                tables.append(ParsedTable(name, rows[0], tuple(rows[1:])))
            index = end
        index += 1
    return ParsedSource(DataSourceType.MARKDOWN, tuple(tables))


def _table_rows(tokens: list[Token]) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    current: list[str] | None = None
    for index, token in enumerate(tokens):
        if token.type == "tr_open":
            current = []
        elif token.type in {"th_open", "td_open"} and current is not None:
            current.append(_next_inline(tokens, index))
        elif token.type == "tr_close" and current is not None:
            rows.append(tuple(current))
            current = None
    return rows


def _next_inline(tokens: list[Token], index: int) -> str:
    for token in tokens[index + 1 :]:
        if token.type == "inline":
            return token.content.strip()
        if token.type.endswith("_close"):
            break
    return ""


def _find_close(tokens: list[Token], start: int, close_type: str) -> int:
    for index in range(start + 1, len(tokens)):
        if tokens[index].type == close_type:
            return index
    return len(tokens) - 1


def _unique_name(heading: str | None, index: int, used: set[str]) -> str:
    base = re.sub(r"[^\w.-]+", "_", heading or "", flags=re.UNICODE).strip("_")
    base = base or f"table_{index + 1}"
    name = base
    suffix = 2
    while name in used:
        name = f"{base}_{suffix}"
        suffix += 1
    return name
