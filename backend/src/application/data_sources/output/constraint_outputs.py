"""Typed application outputs for data-source column constraints."""

from dataclasses import dataclass
from typing import TypeAlias

from src.domain.data_source.constraints import (
    CheckConstraint,
    ColumnConstraint,
    DefaultConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from src.domain.data_source.enums import ColumnConstraintType
from src.domain.shared.types import JsonScalar


@dataclass(frozen=True, slots=True)
class ForeignKeyConstraintOutput:
    type: ColumnConstraintType
    reference_table: str
    reference_column: str


@dataclass(frozen=True, slots=True)
class UniqueConstraintOutput:
    type: ColumnConstraintType


@dataclass(frozen=True, slots=True)
class CheckConstraintOutput:
    type: ColumnConstraintType
    expression: str


@dataclass(frozen=True, slots=True)
class DefaultConstraintOutput:
    type: ColumnConstraintType
    value: JsonScalar


ColumnConstraintOutput: TypeAlias = (
    ForeignKeyConstraintOutput | UniqueConstraintOutput | CheckConstraintOutput | DefaultConstraintOutput
)


def constraint_output(constraint: ColumnConstraint) -> ColumnConstraintOutput:
    """Map one domain constraint onto its stable application union."""
    if isinstance(constraint, ForeignKeyConstraint):
        return ForeignKeyConstraintOutput(
            constraint.type, constraint.reference_table, constraint.reference_column
        )
    if isinstance(constraint, UniqueConstraint):
        return UniqueConstraintOutput(constraint.type)
    if isinstance(constraint, CheckConstraint):
        return CheckConstraintOutput(constraint.type, constraint.expression)
    if isinstance(constraint, DefaultConstraint):
        return DefaultConstraintOutput(constraint.type, constraint.value)
    raise TypeError(f"Constraint không được hỗ trợ: {type(constraint).__name__}")
