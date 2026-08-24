"""Ánh xạ constraint input sang Domain value object."""

from src.application.data_sources.input import (
    CheckConstraintInput,
    ColumnConstraintInput,
    DefaultConstraintInput,
    ForeignKeyConstraintInput,
    UniqueConstraintInput,
)
from src.domain.data_source.constraints import (
    CheckConstraint,
    ColumnConstraint,
    DefaultConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
)


def map_constraints(
    constraints: tuple[ColumnConstraintInput, ...] | None,
) -> tuple[ColumnConstraint, ...] | None:
    """Chuyển constraint input có kiểu rõ ràng sang Domain."""
    if constraints is None:
        return None
    return tuple(_map_constraint(item) for item in constraints)


def _map_constraint(item: ColumnConstraintInput) -> ColumnConstraint:
    if isinstance(item, ForeignKeyConstraintInput):
        return ForeignKeyConstraint(item.reference_table, item.reference_column)
    if isinstance(item, UniqueConstraintInput):
        return UniqueConstraint()
    if isinstance(item, CheckConstraintInput):
        return CheckConstraint(item.expression)
    if isinstance(item, DefaultConstraintInput):
        return DefaultConstraint(item.value)
    raise TypeError(f"Constraint input không được hỗ trợ: {type(item).__name__}")
