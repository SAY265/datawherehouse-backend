"""Output models của application service Project."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class ProjectOutput:
    """Project vừa tạo được phép đi qua application boundary."""

    project_id: EntityID
    domain: str
    target_dialect: str
    status: str
    created_at: datetime
    name: str = ""


@dataclass(frozen=True)
class ProjectSummaryOutput:
    project_id: EntityID
    name: str
    domain: str
    status: str
    updated_at: datetime


@dataclass(frozen=True)
class ProjectDetailOutput:
    """Chi tiết đầy đủ của một project."""

    project_id: EntityID
    name: str
    domain: str
    description: str | None
    requirement: str
    status: str
    target_dialect: str
    created_at: datetime
    updated_at: datetime
    revision: int = 1


__all__ = ["ProjectDetailOutput", "ProjectOutput", "ProjectSummaryOutput"]
