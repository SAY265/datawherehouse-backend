"""Record Pydantic dùng riêng cho JSONB SchemaMetadata."""

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field
from src.domain.data_source.enums import ColumnConstraintType, ColumnDataType, RelationshipType
from src.domain.shared.types import JsonScalar


class _ConstraintRecord(BaseModel):
    """Cấu hình chung cho record constraint."""

    model_config = ConfigDict(extra="forbid")


class ForeignKeyConstraintRecord(_ConstraintRecord):
    """Record constraint khóa ngoại."""

    type: Literal[ColumnConstraintType.FOREIGN_KEY]
    reference_table: str
    reference_column: str


class UniqueConstraintRecord(_ConstraintRecord):
    """Record constraint duy nhất."""

    type: Literal[ColumnConstraintType.UNIQUE]


class CheckConstraintRecord(_ConstraintRecord):
    """Record constraint kiểm tra."""

    type: Literal[ColumnConstraintType.CHECK]
    expression: str


class DefaultConstraintRecord(_ConstraintRecord):
    """Record constraint giá trị mặc định."""

    type: Literal[ColumnConstraintType.DEFAULT]
    value: JsonScalar


ConstraintRecord: TypeAlias = Annotated[
    ForeignKeyConstraintRecord | UniqueConstraintRecord | CheckConstraintRecord | DefaultConstraintRecord,
    Field(discriminator="type"),
]


class ColumnRecord(BaseModel):
    """Record metadata cột theo contract hiện hành."""

    model_config = ConfigDict(extra="forbid")
    name: str
    data_type: ColumnDataType
    primary_key: bool = False
    nullable: bool = True
    constraints: list[ConstraintRecord] = Field(default_factory=list)
    description: str | None = None
    null_count: int = Field(default=0, ge=0)
    distinct_count: int = Field(default=0, ge=0)
    distinct_values: list[JsonScalar] = Field(default_factory=list)
    is_unique_candidate: bool = False
    is_key_candidate: bool = False


class TableRecord(BaseModel):
    """Record của một bảng trong schema JSONB."""

    model_config = ConfigDict(extra="forbid")
    name: str
    columns: list[ColumnRecord] = Field(default_factory=list)


class RelationshipRecord(BaseModel):
    """Record của một quan hệ trong schema JSONB."""

    model_config = ConfigDict(extra="forbid")
    from_column: str
    to_column: str
    type: RelationshipType


class SchemaRecord(BaseModel):
    """Record gốc được kiểm tra nghiêm ngặt trước khi decode."""

    model_config = ConfigDict(extra="forbid")
    tables: list[TableRecord] = Field(default_factory=list)
    relationships: list[RelationshipRecord] = Field(default_factory=list)
