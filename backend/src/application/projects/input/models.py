"""Input models độc lập HTTP cho các thao tác Project."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class CreateProjectInput:
    """Dữ liệu tạo Project; Data Source có use case riêng."""

    name: str
    requirement: str | None = None
    domain: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateProjectInput:
    """Dữ liệu thay thế thông tin thuộc Project."""

    project_id: EntityID
    name: str
    requirement: str | None = None
    domain: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectIdInput:
    """Input cho thao tác trên một Project cụ thể."""

    project_id: EntityID
