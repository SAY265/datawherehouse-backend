"""Quy tắc nghiệp vụ cho miền Yêu cầu (Requirement)."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

MAX_REQUIREMENT_TITLE_LENGTH = 255


def validate_requirement_fields(title: str, description: str) -> None:
    """Kiểm tra tính hợp lệ tiêu đề và mô tả của Yêu cầu.

    Args:
        title: Tiêu đề yêu cầu.
        description: Mô tả chi tiết của yêu cầu.
    """
    if not title or not title.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_REQUIREMENT_TITLE,
            message="Tiêu đề yêu cầu không được để trống.",
        )
    if len(title.strip()) > MAX_REQUIREMENT_TITLE_LENGTH:
        raise BusinessException(
            code=ErrorCode.REQUIREMENT_TITLE_TOO_LONG,
            message=f"Tiêu đề yêu cầu vượt quá độ dài tối đa ({MAX_REQUIREMENT_TITLE_LENGTH} ký tự).",
        )
    if not description or not description.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_REQUIREMENT_DESCRIPTION,
            message="Mô tả yêu cầu không được để trống.",
        )
