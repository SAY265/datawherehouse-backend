"""Build a selected-table preview from an already parsed structured source."""

from src.application.data_sources.output import PreviewOutput
from src.infrastructure.storage.tabular_source_models import ParsedSource

MAX_PREVIEW_ROWS = 5


def structured_preview(source: ParsedSource, table_name: str | None) -> PreviewOutput:
    """Select a table and return normalized string rows plus available names."""
    available = tuple(table.name for table in source.tables)
    selected_name = table_name or available[0]
    table = next((item for item in source.tables if item.name == selected_name), None)
    if table is None:
        raise ValueError(f"Không tìm thấy table {selected_name}.")
    rows = tuple(
        {
            name: None if value is None else str(value)
            for name, value in zip(table.columns, row, strict=True)
        }
        for row in table.rows[:MAX_PREVIEW_ROWS]
    )
    return PreviewOutput(table.name, available, rows, len(table.rows))
