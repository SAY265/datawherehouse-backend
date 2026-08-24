"""HTTP-independent output models for the Data Source application service."""

from dataclasses import dataclass

from src.application.data_sources.output.constraint_outputs import (
    ColumnConstraintOutput,
    constraint_output,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import ColumnDataType, DataSourceAnalysisStatus, DataSourceType
from src.domain.data_source.value_objects import ColumnMetadata, TableMetadata
from src.domain.shared.types import EntityID, JsonScalar


@dataclass(frozen=True, slots=True)
class DataSourceColumnOutput:
    name: str
    data_type: ColumnDataType
    nullable: bool
    primary_key: bool
    null_count: int
    distinct_count: int
    distinct_values: tuple[JsonScalar, ...]
    constraints: tuple[ColumnConstraintOutput, ...]
    is_unique_candidate: bool
    is_key_candidate: bool

    @classmethod
    def from_domain(cls, column: ColumnMetadata) -> "DataSourceColumnOutput":
        return cls(
            name=column.name,
            data_type=column.data_type,
            nullable=column.nullable,
            primary_key=column.primary_key,
            null_count=column.null_count,
            distinct_count=column.distinct_count,
            distinct_values=column.distinct_values,
            constraints=tuple(constraint_output(item) for item in column.constraints),
            is_unique_candidate=column.is_unique_candidate,
            is_key_candidate=column.is_key_candidate,
        )


@dataclass(frozen=True, slots=True)
class DataSourceTableOutput:
    name: str
    columns: tuple[DataSourceColumnOutput, ...]

    @classmethod
    def from_domain(cls, table: TableMetadata) -> "DataSourceTableOutput":
        return cls(
            name=table.name,
            columns=tuple(DataSourceColumnOutput.from_domain(item) for item in table.columns),
        )


@dataclass(frozen=True, slots=True)
class DataSourceOutput:
    id: EntityID
    project_id: EntityID
    name: str
    type: DataSourceType
    description: str | None
    tables: tuple[DataSourceTableOutput, ...]
    analysis_status: DataSourceAnalysisStatus

    @classmethod
    def from_domain(cls, source: DataSource) -> "DataSourceOutput":
        tables = source.schema_metadata.tables if source.schema_metadata else ()
        status = (
            DataSourceAnalysisStatus.READY
            if source.schema_metadata is not None
            else DataSourceAnalysisStatus.PENDING
        )
        return cls(
            id=source.id,
            project_id=source.project_id,
            name=source.name,
            type=source.type,
            description=source.description,
            tables=tuple(DataSourceTableOutput.from_domain(table) for table in tables),
            analysis_status=status,
        )


@dataclass(frozen=True, slots=True)
class PreviewOutput:
    table_name: str
    available_tables: tuple[str, ...]
    rows: tuple[dict[str, str | None], ...]
    total_rows: int


@dataclass(frozen=True, slots=True)
class DataSourceListOutput:
    items: tuple[DataSourceOutput, ...]
    can_edit: bool


@dataclass(frozen=True, slots=True)
class UploadDataSourcesOutput:
    data_sources: tuple[DataSourceOutput, ...]
    total_files_uploaded: int
