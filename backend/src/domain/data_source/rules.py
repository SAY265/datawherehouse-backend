"""Quy tắc nghiệp vụ cho miền Nguồn dữ liệu (Data Source)."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

MAX_DATA_SOURCE_NAME_LENGTH = 255


def validate_data_source_fields(name: str, location: str) -> None:
    """Kiểm tra tính hợp lệ của Nguồn dữ liệu.

    Args:
        name: Tên nguồn dữ liệu.
        location: Đường dẫn hoặc địa điểm lưu trữ dữ liệu.
    """
    if not name or not name.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_DATA_SOURCE_NAME,
            message="Tên nguồn dữ liệu không được để trống.",
        )
    if len(name.strip()) > MAX_DATA_SOURCE_NAME_LENGTH:
        raise BusinessException(
            code=ErrorCode.DATA_SOURCE_NAME_TOO_LONG,
            message=f"Tên nguồn dữ liệu vượt quá độ dài tối đa ({MAX_DATA_SOURCE_NAME_LENGTH} ký tự).",
        )
    if not location or not location.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_DATA_SOURCE_LOCATION,
            message="Đường dẫn lưu trữ nguồn dữ liệu (location) không được để trống.",
        )
