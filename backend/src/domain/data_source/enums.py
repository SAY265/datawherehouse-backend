"""Các kiểu liệt kê (Enums) thuộc miền Nguồn dữ liệu (Data Source)."""

from enum import StrEnum


class DataSourceType(StrEnum):
    """Định dạng loại Nguồn dữ liệu (Data Source Type)."""

    CSV = "CSV"
    EXCEL = "EXCEL"
    JSON = "JSON"
    SQL = "SQL"
    TEXT = "TEXT"


class RelationshipType(StrEnum):
    """Loại mối quan hệ giữa các bảng trong cơ sở dữ liệu."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
