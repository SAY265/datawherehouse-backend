"""Output models độc lập HTTP cho các thao tác Project."""

from dataclasses import dataclass
from datetime import datetime

from src.application.data_sources.output import DataSourceOutput
from src.application.requirements.output import RequirementOutput
from src.domain.data_source.entities import DataSource
from src.domain.project.entities import Project
from src.domain.project.enums import ProjectStatus
from src.domain.requirement.entities import Requirement
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ProjectSummaryOutput:
    """Dữ liệu gọn cho danh sách Project."""

    id: EntityID
    name: str
    user_id: EntityID
    status: ProjectStatus
    domain: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    data_source_count: int
    is_data_model_outdated: bool = False

    @classmethod
    def from_domain(
        cls,
        project: Project,
        data_source_count: int,
        is_data_model_outdated: bool = False,
    ) -> "ProjectSummaryOutput":
        """Ánh xạ Project và source count sang summary output."""
        return cls(
            id=project.id,
            name=project.name,
            user_id=project.user_id,
            status=project.status,
            domain=project.domain,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            data_source_count=data_source_count,
            is_data_model_outdated=is_data_model_outdated,
        )


@dataclass(frozen=True, slots=True)
class ProjectOutput:
    """Dữ liệu chi tiết Project và metadata nguồn dữ liệu."""

    summary: ProjectSummaryOutput
    requirement: str | None = None
    requirements: tuple[RequirementOutput, ...] = ()
    data_sources: tuple[DataSourceOutput, ...] = ()

    @classmethod
    def from_domain(
        cls,
        project: Project,
        sources: tuple[DataSource, ...],
        requirements: tuple[Requirement, ...],
    ) -> "ProjectOutput":
        """Ánh xạ aggregate Project sang application output chi tiết."""
        summary = ProjectSummaryOutput.from_domain(project, len(sources))
        return cls(
            summary=summary,
            requirement=project.requirement,
            requirements=tuple(RequirementOutput.from_domain(item) for item in requirements),
            data_sources=tuple(DataSourceOutput.from_domain(item) for item in sources),
        )
