"""Application service duy nhất của module Requirement."""

from src.application.requirements.i_requirement_service import IRequirementService


class RequirementService(IRequirementService):
    """Điểm hiện thực tập trung cho các use case Requirement."""
