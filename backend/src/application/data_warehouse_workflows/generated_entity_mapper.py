"""Ánh xạ typed Agent output sang Domain entity đã kiểm tra."""

from src.application.data_warehouse_workflows.output import (
    GeneratedAnalyticalRequirement,
    GeneratedRequirement,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID


def map_generated_requirements(
    project_id: EntityID, items: tuple[GeneratedRequirement, ...]
) -> tuple[Requirement, ...]:
    """Tạo Requirements mới từ structured output."""
    try:
        return tuple(
            Requirement(
                project_id=project_id,
                title=item.title,
                description=item.description,
                type=RequirementType(item.requirement_type.upper()),
                priority=RequirementPriority(item.priority.upper()),
            )
            for item in items
        )
    except ValueError as exc:
        raise BusinessException(
            ErrorCode.INVALID_REQUIREMENT, "RequirementAgent trả enum không hợp lệ."
        ) from exc


def map_generated_analytical(
    items: tuple[GeneratedAnalyticalRequirement, ...], valid_ids: set[EntityID]
) -> tuple[AnalyticalRequirement, ...]:
    """Tạo AnalyticalRequirements và từ chối source ID không xác định."""
    if any(item.source_requirement_id not in valid_ids for item in items):
        raise BusinessException(
            ErrorCode.INVALID_ANALYTICAL_REQUIREMENT_REF,
            "RequirementAgent trả source_requirement_id không thuộc dự án.",
        )
    try:
        return tuple(_to_analytical(item) for item in items)
    except ValueError as exc:
        raise BusinessException(
            ErrorCode.INVALID_ANALYTICAL_REQUIREMENT_REF,
            "RequirementAgent trả aggregation_method không hợp lệ.",
        ) from exc


def _to_analytical(item: GeneratedAnalyticalRequirement) -> AnalyticalRequirement:
    """Ánh xạ một output đã có source ID hợp lệ."""
    return AnalyticalRequirement(
        requirement_id=item.source_requirement_id,
        metric=item.metric,
        dimension=item.dimension,
        time_granularity=item.time_granularity,
        aggregation_method=AggregationMethod(item.aggregation_method.upper()),
        grain=item.grain,
    )
