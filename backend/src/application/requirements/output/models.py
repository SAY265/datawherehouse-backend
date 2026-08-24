"""Output model cho các thao tác Requirement."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class RequirementOutput:
    """Snapshot Requirement được phép đi qua application boundary."""

    id: EntityID
    project_id: EntityID
    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, requirement: Requirement) -> "RequirementOutput":
        """Ánh xạ domain entity sang application output."""
        return cls(
            id=requirement.id,
            project_id=requirement.project_id,
            title=requirement.title,
            description=requirement.description,
            type=requirement.type,
            priority=requirement.priority,
            created_at=requirement.created_at,
            updated_at=requirement.updated_at,
        )
