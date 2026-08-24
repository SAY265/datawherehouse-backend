"""Small pure helpers shared by workflow analysis orchestration."""

from src.application.data_warehouse_workflows.input import RequirementContext
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.requirement.entities import Requirement


def ensure_revision(current: int, expected: int) -> None:
    """Reject persistence when an Agent input changed while it was running."""
    if current != expected:
        raise BusinessException(
            ErrorCode.ANALYSIS_INPUT_CHANGED,
            "Input đã thay đổi trong lúc Agent đang xử lý.",
        )


def to_requirement_context(requirement: Requirement) -> RequirementContext:
    """Expose only requirement fields consumed by the Agent."""
    return RequirementContext(
        requirement.id,
        requirement.title,
        requirement.description,
        requirement.type.value,
        requirement.priority.value,
    )
