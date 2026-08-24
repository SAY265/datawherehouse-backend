"""Module quản lý Yêu cầu Phân tích (Analytical Requirement Domain)."""

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.analytical_requirement.repository import IAnalyticalRequirementRepository
from src.domain.analytical_requirement.rules import validate_analytical_requirement

__all__: list[str] = [
    "AnalyticalRequirement",
    "AggregationMethod",
    "IAnalyticalRequirementRepository",
    "validate_analytical_requirement",
]
