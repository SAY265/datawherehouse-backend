"""Input models độc lập HTTP cho Data Source application service."""

from dataclasses import dataclass, field
from typing import TypeAlias

from src.domain.data_source.enums import ColumnDataType
from src.domain.shared.types import EntityID, JsonScalar


@dataclass(frozen=True, slots=True)
class ListDataSourcesInput:
    """Input liệt kê nguồn dữ liệu của dự án."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class DataSourceIdInput:
    """Input định danh một nguồn trong dự án."""

    project_id: EntityID
    data_source_id: EntityID


@dataclass(frozen=True, slots=True)
class DataSourcePreviewInput:
    """Input preview một table tùy chọn trong Data Source."""

    project_id: EntityID
    data_source_id: EntityID
    table_name: str | None = None


@dataclass(frozen=True, slots=True)
class UploadFileInput:
    """Nội dung file đã được đọc tại HTTP boundary."""

    filename: str
    content: bytes


@dataclass(frozen=True, slots=True)
class UploadDataSourcesInput:
    """Input upload một batch CSV."""

    project_id: EntityID
    files: tuple[UploadFileInput, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ForeignKeyConstraintInput:
    """Input constraint khóa ngoại."""

    reference_table: str
    reference_column: str


@dataclass(frozen=True, slots=True)
class UniqueConstraintInput:
    """Input constraint duy nhất."""


@dataclass(frozen=True, slots=True)
class CheckConstraintInput:
    """Input constraint kiểm tra."""

    expression: str


@dataclass(frozen=True, slots=True)
class DefaultConstraintInput:
    """Input constraint giá trị mặc định."""

    value: JsonScalar


ColumnConstraintInput: TypeAlias = (
    ForeignKeyConstraintInput | UniqueConstraintInput | CheckConstraintInput | DefaultConstraintInput
)


@dataclass(frozen=True, slots=True)
class DataSourceColumnTargetInput:
    """Định danh đầy đủ của một cột nguồn."""

    project_id: EntityID
    data_source_id: EntityID
    table_name: str
    column_name: str


@dataclass(frozen=True, slots=True)
class UpdateDataSourceColumnInput:
    """Các field metadata cần cập nhật một phần."""

    target: DataSourceColumnTargetInput
    data_type: ColumnDataType | None = None
    distinct_values: tuple[JsonScalar, ...] | None = None
    constraints: tuple[ColumnConstraintInput, ...] | None = None
