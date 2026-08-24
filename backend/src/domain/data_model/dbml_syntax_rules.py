"""Invariant nội dung DBML thuần của Domain."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode


def validate_dbml(dbml: str) -> None:
    """Xác nhận nội dung DBML không rỗng tại Domain boundary.

    Args:
        dbml: Nội dung DBML cần kiểm tra.

    Raises:
        BusinessException: Khi nội dung rỗng.
    """
    if not isinstance(dbml, str) or not dbml.strip():
        raise BusinessException(
            code=ErrorCode.DATA_MODEL_DBML_REQUIRED,
            message="Nội dung DBML không được để trống.",
        )
