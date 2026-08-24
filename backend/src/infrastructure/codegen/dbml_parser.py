"""Facade bắt buộc dùng PyDBML để phân tích DBML."""

from pydbml import PyDBML
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode


def parse_dbml(dbml: str) -> PyDBML:
    """Phân tích DBML và dịch lỗi cú pháp sang lỗi nghiệp vụ."""
    try:
        return PyDBML(dbml)
    except Exception as exc:
        raise BusinessException(
            code=ErrorCode.DATA_MODEL_DBML_SYNTAX_INVALID,
            message="Không thể phân tích cú pháp DBML.",
        ) from exc
