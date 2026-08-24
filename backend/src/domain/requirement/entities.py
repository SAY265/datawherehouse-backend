"""Thực thể Yêu cầu (Requirement Entity)."""

from dataclasses import dataclass, field
from uuid import uuid4

from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.requirement.rules import validate_requirement_fields
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass
class Requirement(BaseEntity):
    """Thực thể đại diện cho Yêu cầu (Requirement) trong hệ thống."""

    project_id: EntityID = field(default_factory=uuid4)
    type: RequirementType = RequirementType.BUSINESS
    title: str = ""
    description: str = ""
    priority: RequirementPriority = RequirementPriority.MEDIUM

    def __post_init__(self) -> None:
        """Thực thi kiểm tra quy tắc nghiệp vụ cho Yêu cầu."""
        super().__post_init__()
        validate_requirement_fields(self.title, self.description)
