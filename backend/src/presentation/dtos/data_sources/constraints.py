"""Wire models dùng chung cho constraint cột Data Source."""

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_sources.input import (
    CheckConstraintInput,
    ColumnConstraintInput,
    DefaultConstraintInput,
    ForeignKeyConstraintInput,
    UniqueConstraintInput,
)
from src.domain.data_source.enums import ColumnConstraintType
from src.domain.shared.types import JsonScalar


class _ConstraintDto(BaseModel):
    """Cấu hình validation chung cho constraint DTO."""

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
    )

    def to_application(self) -> ColumnConstraintInput:
        """Ánh xạ wire model sang application input."""
        raise NotImplementedError


class ForeignKeyConstraintDto(_ConstraintDto):
    """Constraint khóa ngoại."""

    type: Literal[ColumnConstraintType.FOREIGN_KEY] = Field(description="Loại constraint")
    reference_table: str = Field(min_length=1, description="Bảng được tham chiếu")
    reference_column: str = Field(min_length=1, description="Cột được tham chiếu")

    def to_application(self) -> ForeignKeyConstraintInput:
        """Ánh xạ constraint khóa ngoại."""
        return ForeignKeyConstraintInput(self.reference_table, self.reference_column)


class UniqueConstraintDto(_ConstraintDto):
    """Constraint duy nhất."""

    type: Literal[ColumnConstraintType.UNIQUE] = Field(description="Loại constraint")

    def to_application(self) -> UniqueConstraintInput:
        """Ánh xạ constraint duy nhất."""
        return UniqueConstraintInput()


class CheckConstraintDto(_ConstraintDto):
    """Constraint kiểm tra."""

    type: Literal[ColumnConstraintType.CHECK] = Field(description="Loại constraint")
    expression: str = Field(min_length=1, description="Biểu thức CHECK chính thức")

    def to_application(self) -> CheckConstraintInput:
        """Ánh xạ constraint kiểm tra."""
        return CheckConstraintInput(self.expression)


class DefaultConstraintDto(_ConstraintDto):
    """Constraint giá trị mặc định."""

    type: Literal[ColumnConstraintType.DEFAULT] = Field(description="Loại constraint")
    value: JsonScalar = Field(description="Giá trị mặc định hoặc biểu thức dạng chuỗi")

    def to_application(self) -> DefaultConstraintInput:
        """Ánh xạ constraint giá trị mặc định."""
        return DefaultConstraintInput(self.value)


ColumnConstraintDto: TypeAlias = Annotated[
    ForeignKeyConstraintDto | UniqueConstraintDto | CheckConstraintDto | DefaultConstraintDto,
    Field(discriminator="type"),
]
