"""Quy tắc chuẩn hóa thông tin mô tả Project."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.string import normalize_whitespace, safe_strip

MIN_PROJECT_NAME_LENGTH = 3
MAX_PROJECT_NAME_LENGTH = 255
MIN_PROJECT_REQUIREMENT_LENGTH = 10
MAX_PROJECT_DOMAIN_LENGTH = 100


def normalize_project_name(name: str) -> str:
    """Chuẩn hóa và kiểm tra tên dự án.

    Args:
        name: Tên dự án cần chuẩn hóa.

    Returns:
        Tên dự án đã chuẩn hóa khoảng trắng.

    Raises:
        BusinessException: Khi độ dài tên không hợp lệ.
    """
    normalized = normalize_whitespace(name)
    if len(normalized) < MIN_PROJECT_NAME_LENGTH:
        _raise(ErrorCode.INVALID_PROJECT_NAME, "Tên dự án phải có ít nhất 3 ký tự.")
    if len(normalized) > MAX_PROJECT_NAME_LENGTH:
        _raise(ErrorCode.PROJECT_NAME_TOO_LONG, "Tên dự án không được vượt quá 255 ký tự.")
    return normalized


def normalize_project_requirement(requirement: str | None) -> str | None:
    """Chuẩn hóa và kiểm tra yêu cầu nghiệp vụ thô.

    Args:
        requirement: Yêu cầu nghiệp vụ do người dùng nhập.

    Returns:
        Yêu cầu đã chuẩn hóa khoảng trắng.

    Raises:
        BusinessException: Khi yêu cầu quá ngắn.
    """
    if requirement is None or not requirement.strip():
        return None
    normalized = normalize_whitespace(requirement)
    if len(normalized) < MIN_PROJECT_REQUIREMENT_LENGTH:
        _raise(
            ErrorCode.INVALID_PROJECT_REQUIREMENT,
            "Yêu cầu nghiệp vụ phải có ít nhất 10 ký tự.",
        )
    return normalized


def normalize_project_domain(domain: str | None) -> str | None:
    """Chuẩn hóa domain tùy chọn và bảo vệ giới hạn lưu trữ.

    Args:
        domain: Lĩnh vực nghiệp vụ tùy chọn.

    Returns:
        Lĩnh vực đã trim hoặc ``None`` khi rỗng.

    Raises:
        BusinessException: Khi lĩnh vực vượt giới hạn lưu trữ.
    """
    normalized = safe_strip(domain)
    if normalized == "":
        return None
    if normalized is not None and len(normalized) > MAX_PROJECT_DOMAIN_LENGTH:
        _raise(ErrorCode.INVALID_PROJECT_DOMAIN, "Lĩnh vực nghiệp vụ vượt quá 100 ký tự.")
    return normalized


def _raise(code: ErrorCode, message: str) -> None:
    """Ném lỗi nghiệp vụ cho thông tin Project không hợp lệ."""
    raise BusinessException(code=code, message=message)
