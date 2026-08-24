"""Bidirectional codec between domain constraints and typed JSONB records."""

from src.domain.data_source.constraints import (
    CheckConstraint,
    ColumnConstraint,
    DefaultConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from src.infrastructure.database.mappers.data_source.schema_metadata_records import (
    CheckConstraintRecord,
    ConstraintRecord,
    DefaultConstraintRecord,
    ForeignKeyConstraintRecord,
    UniqueConstraintRecord,
)


def constraint_to_record(constraint: ColumnConstraint) -> ConstraintRecord:
    """Map a domain constraint onto its JSONB record union."""
    if isinstance(constraint, ForeignKeyConstraint):
        return ForeignKeyConstraintRecord(
            type=constraint.type,
            reference_table=constraint.reference_table,
            reference_column=constraint.reference_column,
        )
    if isinstance(constraint, UniqueConstraint):
        return UniqueConstraintRecord(type=constraint.type)
    if isinstance(constraint, CheckConstraint):
        return CheckConstraintRecord(type=constraint.type, expression=constraint.expression)
    if isinstance(constraint, DefaultConstraint):
        return DefaultConstraintRecord(type=constraint.type, value=constraint.value)
    raise TypeError(f"Constraint không được hỗ trợ: {type(constraint).__name__}")


def record_to_constraint(record: ConstraintRecord) -> ColumnConstraint:
    """Restore a domain constraint from its validated JSONB record."""
    if isinstance(record, ForeignKeyConstraintRecord):
        return ForeignKeyConstraint(record.reference_table, record.reference_column)
    if isinstance(record, UniqueConstraintRecord):
        return UniqueConstraint()
    if isinstance(record, CheckConstraintRecord):
        return CheckConstraint(record.expression)
    if isinstance(record, DefaultConstraintRecord):
        return DefaultConstraint(record.value)
    raise TypeError(f"Constraint record không được hỗ trợ: {type(record).__name__}")
