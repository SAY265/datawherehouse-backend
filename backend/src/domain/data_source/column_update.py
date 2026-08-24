"""Value Object mô tả một lần chỉnh sửa metadata cột."""

from dataclasses import dataclass

from src.domain.data_source.constraints import (
    ColumnConstraint,
    normalize_column_constraints,
)
from src.domain.data_source.enums import ColumnDataType
from src.domain.data_source.rules import normalize_column_update
from src.domain.shared.types import JsonScalar
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class ColumnUpdate(BaseValueObject):
    """Yêu cầu cập nhật kiểu và semantic của một cột trong schema."""

    table_name: str
    column_name: str
    data_type: ColumnDataType | str | None = None
    distinct_values: tuple[JsonScalar, ...] | None = None
    constraints: tuple[ColumnConstraint, ...] | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa và bảo vệ invariant của thao tác cập nhật cột."""
        table, column, data_type = normalize_column_update(self.table_name, self.column_name, self.data_type)
        object.__setattr__(self, "table_name", table)
        object.__setattr__(self, "column_name", column)
        object.__setattr__(self, "data_type", data_type)
        if self.distinct_values is not None:
            object.__setattr__(self, "distinct_values", tuple(self.distinct_values))
        if self.constraints is not None:
            object.__setattr__(
                self,
                "constraints",
                normalize_column_constraints(self.constraints),
            )
