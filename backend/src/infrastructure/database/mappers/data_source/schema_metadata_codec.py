"""Codec JSONB nghiêm ngặt cho SchemaMetadata."""

from pydantic import ValidationError
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source import value_objects as source_values
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.data_source.constraint_codec import (
    constraint_to_record,
    record_to_constraint,
)
from src.infrastructure.database.mappers.data_source.schema_metadata_records import (
    ColumnRecord,
    RelationshipRecord,
    SchemaRecord,
    TableRecord,
)


def encode_schema_metadata(
    schema: source_values.SchemaMetadata | None,
) -> dict[str, JsonValue] | None:
    """Chuyển SchemaMetadata thành payload JSONB."""
    if schema is None:
        return None
    record = SchemaRecord(
        tables=[_table_to_record(table) for table in schema.tables],
        relationships=[
            RelationshipRecord(
                from_column=item.from_column,
                to_column=item.to_column,
                type=item.type,
            )
            for item in schema.relationships
        ],
    )
    return record.model_dump(mode="json")


def decode_schema_metadata(
    payload: dict[str, JsonValue] | None,
) -> source_values.SchemaMetadata | None:
    """Khôi phục SchemaMetadata và báo lỗi khi JSONB bị hỏng."""
    if payload is None:
        return None
    try:
        record = SchemaRecord.model_validate(payload)
    except ValidationError as exc:
        raise InfrastructureException(
            code=ErrorCode.DATABASE_ERROR,
            message="Metadata nguồn dữ liệu trong cơ sở dữ liệu không hợp lệ.",
        ) from exc
    return source_values.SchemaMetadata(
        tables=tuple(_record_to_table(table) for table in record.tables),
        relationships=tuple(
            source_values.RelationshipMetadata(item.from_column, item.to_column, item.type)
            for item in record.relationships
        ),
    )


def _table_to_record(table: source_values.TableMetadata) -> TableRecord:
    """Chuyển metadata bảng sang JSONB record."""
    return TableRecord(
        name=table.name,
        columns=[_column_to_record(column) for column in table.columns],
    )


def _column_to_record(column: source_values.ColumnMetadata) -> ColumnRecord:
    """Chuyển metadata cột sang record typed."""
    return ColumnRecord(
        name=column.name,
        data_type=column.data_type,
        primary_key=column.primary_key,
        nullable=column.nullable,
        constraints=[constraint_to_record(item) for item in column.constraints],
        description=column.description,
        null_count=column.null_count,
        distinct_count=column.distinct_count,
        distinct_values=list(column.distinct_values),
        is_unique_candidate=column.is_unique_candidate,
        is_key_candidate=column.is_key_candidate,
    )


def _record_to_table(record: TableRecord) -> source_values.TableMetadata:
    """Khôi phục metadata bảng từ record."""
    return source_values.TableMetadata(
        name=record.name,
        columns=tuple(_record_to_column(column) for column in record.columns),
    )


def _record_to_column(record: ColumnRecord) -> source_values.ColumnMetadata:
    """Khôi phục metadata cột từ schema mới."""
    return source_values.ColumnMetadata(
        name=record.name,
        data_type=record.data_type,
        primary_key=record.primary_key,
        nullable=record.nullable,
        constraints=tuple(record_to_constraint(item) for item in record.constraints),
        description=record.description,
        null_count=record.null_count,
        distinct_count=record.distinct_count,
        distinct_values=tuple(record.distinct_values),
        is_unique_candidate=record.is_unique_candidate,
        is_key_candidate=record.is_key_candidate,
    )
