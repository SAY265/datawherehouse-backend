"""Quy tắc nghiệp vụ cho miền Dự án (Project)."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

MAX_PROJECT_NAME_LENGTH = 255


def validate_project_fields(name: str, requirement: str) -> None:
    """Kiểm tra tính hợp lệ của thông tin dự án.

    Args:
        name: Tên dự án.
        requirement: Nội dung yêu cầu thô nhập bởi người dùng.
    """
    if not name or not name.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_NAME,
            message="Tên dự án không được để trống.",
        )
    if len(name.strip()) > MAX_PROJECT_NAME_LENGTH:
        raise BusinessException(
            code=ErrorCode.PROJECT_NAME_TOO_LONG,
            message=f"Tên dự án vượt quá độ dài tối đa ({MAX_PROJECT_NAME_LENGTH} ký tự).",
        )
    if not requirement or not requirement.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_REQUIREMENT,
            message="Yêu cầu thô (requirement) không được để trống.",
        )
