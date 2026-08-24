"""Thực thể Yêu cầu Phân tích (Analytical Requirement Entity)."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.analytical_requirement.rules import validate_analytical_requirement
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False)
class AnalyticalRequirement(BaseEntity):
    """Thực thể đại diện cho Yêu cầu Phân tích chi tiết (Analytical Requirement)."""

    requirement_id: EntityID = field(default_factory=uuid4)
    metric: str | None = None
    dimension: str | None = None
    time_granularity: str | None = None
    aggregation_method: AggregationMethod | None = None
    grain: str | None = None

    def __post_init__(self) -> None:
        """Thực thi kiểm tra quy tắc nghiệp vụ cho Yêu cầu Phân tích."""
        super().__post_init__()

        if isinstance(self.aggregation_method, str):
            self.aggregation_method = AggregationMethod(self.aggregation_method)

        validate_analytical_requirement(self.requirement_id)
