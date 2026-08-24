"""Module quản lý Nguồn dữ liệu (Data Source Domain)."""

from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType, RelationshipType
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.data_source.rules import validate_data_source_fields
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)

__all__: list[str] = [
    "DataSource",
    "DataSourceType",
    "RelationshipType",
    "SchemaMetadata",
    "TableMetadata",
    "ColumnMetadata",
    "RelationshipMetadata",
    "IDataSourceRepository",
    "validate_data_source_fields",
]
