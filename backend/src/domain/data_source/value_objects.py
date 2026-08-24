"""Value Objects thuộc miền Nguồn dữ liệu (Data Source)."""

from dataclasses import dataclass, field

from src.domain.data_source.enums import RelationshipType
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class ColumnMetadata(BaseValueObject):
    """Value Object đại diện cho metadata và các ràng buộc của một cột trong nguồn dữ liệu."""

    name: str
    data_type: str
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    foreign_key_reference: str | None = None
    default_value: str | None = None
    # Danh sách các ràng buộc khác của cột (VD: age >= 0, age <= 120, ...)
    constraints: tuple[str, ...] = field(default_factory=tuple)
    description: str | None = None  # Mô tả chi tiết về ý nghĩa của cột


@dataclass(frozen=True)
class TableMetadata(BaseValueObject):
    """Value Object đại diện cho metadata của một bảng trong nguồn dữ liệu."""

    name: str
    columns: tuple[ColumnMetadata, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RelationshipMetadata(BaseValueObject):
    """Value Object đại diện cho thông tin mối quan hệ giữa các bảng."""

    from_column: str
    to_column: str
    type: RelationshipType = RelationshipType.MANY_TO_ONE

    def __post_init__(self) -> None:
        """Đảm bảo trường type được parse thành RelationshipType enum nếu khởi tạo từ string."""
        if isinstance(self.type, str):
            object.__setattr__(self, "type", RelationshipType(self.type))


@dataclass(frozen=True)
class SchemaMetadata(BaseValueObject):
    """Value Object đại diện cho cấu trúc metadata đã bóc tách từ nguồn dữ liệu."""

    tables: tuple[TableMetadata, ...] = field(default_factory=tuple)
    relationships: tuple[RelationshipMetadata, ...] = field(default_factory=tuple)
