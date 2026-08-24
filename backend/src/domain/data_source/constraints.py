"""Value objects cho constraint có cấu trúc của cột nguồn."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TypeAlias

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.enums import ColumnConstraintType
from src.domain.shared.types import JsonScalar
from src.domain.shared.value_object import BaseValueObject


def _required(value: str, field_name: str) -> str:
    """Chuẩn hóa chuỗi bắt buộc của constraint."""
    normalized = value.strip()
    if not normalized:
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            f"{field_name} của constraint không được để trống.",
        )
    return normalized


@dataclass(frozen=True)
class ForeignKeyConstraint(BaseValueObject):
    """Constraint tham chiếu một cột thuộc bảng khác."""

    reference_table: str
    reference_column: str
    type: ColumnConstraintType = field(
        default=ColumnConstraintType.FOREIGN_KEY,
        init=False,
    )

    def __post_init__(self) -> None:
        """Chuẩn hóa định danh bảng và cột tham chiếu."""
        object.__setattr__(self, "reference_table", _required(self.reference_table, "Bảng"))
        object.__setattr__(self, "reference_column", _required(self.reference_column, "Cột"))


@dataclass(frozen=True)
class UniqueConstraint(BaseValueObject):
    """Constraint yêu cầu giá trị cột là duy nhất."""

    type: ColumnConstraintType = field(default=ColumnConstraintType.UNIQUE, init=False)


@dataclass(frozen=True)
class CheckConstraint(BaseValueObject):
    """Constraint kiểm tra biểu thức chính thức từ source."""

    expression: str
    type: ColumnConstraintType = field(default=ColumnConstraintType.CHECK, init=False)

    def __post_init__(self) -> None:
        """Chuẩn hóa biểu thức kiểm tra."""
        object.__setattr__(self, "expression", _required(self.expression, "Biểu thức"))


@dataclass(frozen=True)
class DefaultConstraint(BaseValueObject):
    """Constraint mô tả giá trị mặc định của cột."""

    value: JsonScalar
    type: ColumnConstraintType = field(default=ColumnConstraintType.DEFAULT, init=False)


ColumnConstraint: TypeAlias = ForeignKeyConstraint | UniqueConstraint | CheckConstraint | DefaultConstraint


def normalize_column_constraints(
    values: Iterable[ColumnConstraint],
) -> tuple[ColumnConstraint, ...]:
    """Đóng băng và từ chối constraint không thuộc discriminated union."""
    constraints = tuple(values)
    allowed = (
        ForeignKeyConstraint,
        UniqueConstraint,
        CheckConstraint,
        DefaultConstraint,
    )
    if not all(isinstance(item, allowed) for item in constraints):
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Constraint cột không thuộc schema được hỗ trợ.",
        )
    return constraints
