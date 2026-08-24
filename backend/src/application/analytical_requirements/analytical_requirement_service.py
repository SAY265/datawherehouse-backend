"""Application service duy nhất của module Analytical Requirement."""

from src.application.analytical_requirements.i_analytical_requirement_service import (
    IAnalyticalRequirementService,
)


class AnalyticalRequirementService(IAnalyticalRequirementService):
    """Điểm hiện thực tập trung cho các use case Analytical Requirement."""
