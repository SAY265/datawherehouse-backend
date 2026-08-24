"""Thực thể Nguồn dữ liệu (Data Source Entity)."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.rules import validate_data_source_fields
from src.domain.data_source.value_objects import SchemaMetadata
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False)
class DataSource(BaseEntity):
    """Thực thể đại diện cho Nguồn dữ liệu (Data Source) trong hệ thống."""

    project_id: EntityID = field(default_factory=uuid4)
    name: str = ""
    location: str = ""
    type: DataSourceType = DataSourceType.CSV
    description: str | None = None
    schema_metadata: SchemaMetadata | None = None

    def __post_init__(self) -> None:
        """Thực thi kiểm tra dữ liệu Nguồn dữ liệu."""
        super().__post_init__()
        validate_data_source_fields(self.name, self.location)
