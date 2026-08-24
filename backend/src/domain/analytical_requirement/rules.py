"""Quy tắc nghiệp vụ cho miền Yêu cầu Phân tích (Analytical Requirement)."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.types import EntityID


def validate_analytical_requirement(requirement_id: EntityID) -> None:
    """Kiểm tra tính hợp lệ của tham chiếu Yêu cầu gốc.

    Args:
        requirement_id: Mã UUID của Yêu cầu gốc.
    """
    if not requirement_id:
        raise BusinessException(
            code=ErrorCode.INVALID_ANALYTICAL_REQUIREMENT_REF,
            message="Yêu cầu phân tích phải thuộc về một Yêu cầu (requirement_id) hợp lệ.",
        )
