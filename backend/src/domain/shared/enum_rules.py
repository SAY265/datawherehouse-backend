"""Quy tắc chuẩn hóa enum serialize đi vào Domain."""

from enum import StrEnum
from typing import TypeVar

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

TEnum = TypeVar("TEnum", bound=StrEnum)


def normalize_str_enum(
    value: TEnum | str,
    enum_type: type[TEnum],
    error_code: ErrorCode,
) -> TEnum:
    """Chuẩn hóa chuỗi thành enum và ánh xạ lỗi về Domain exception.

    Args:
        value: Enum hoặc giá trị serialize cần chuẩn hóa.
        enum_type: Lớp enum đích.
        error_code: Mã lỗi hiện có phù hợp bounded context.

    Returns:
        Thành viên enum hợp lệ.

    Raises:
        BusinessException: Khi giá trị không thuộc enum đích.
    """
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        raise BusinessException(
            code=error_code,
            message=f"Giá trị {enum_type.__name__} không hợp lệ.",
        ) from exc
