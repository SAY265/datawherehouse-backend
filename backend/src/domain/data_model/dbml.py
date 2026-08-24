"""Facade tương thích cho việc kiểm tra cú pháp DBML ở tầng domain."""

from src.domain.data_model.rules import validate_dbml


def parse_dbml_schema(source: str) -> None:
    """Kiểm tra DBML và chuẩn hóa lỗi parser thành ``BusinessException``."""
    validate_dbml(source)
