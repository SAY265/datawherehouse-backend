"""Response DTOs cho Project Init."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from src.application.projects.output import (
    ProjectDetailOutput,
    ProjectOutput,
    ProjectSummaryOutput,
)


class ProjectResponse(BaseModel):
    """Project vừa được tạo cùng UUID dùng xuyên suốt workflow."""

    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    name: str = ""
    domain: str
    target_dialect: str
    status: str
    created_at: datetime

    @classmethod
    def from_application(cls, output: ProjectOutput) -> "ProjectResponse":
        return cls.model_validate(output)


class ProjectSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    name: str
    domain: str
    status: str
    updated_at: datetime

    @classmethod
    def from_application(cls, output: ProjectSummaryOutput) -> "ProjectSummaryResponse":
        return cls.model_validate(output)


class ProjectDetailResponse(BaseModel):
    """Thông tin chi tiết của dự án."""

    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    name: str
    domain: str
    description: str | None = None
    requirement: str
    status: str
    target_dialect: str
    created_at: datetime
    updated_at: datetime
    revision: int = 1

    @classmethod
    def from_application(cls, output: ProjectDetailOutput) -> "ProjectDetailResponse":
        return cls.model_validate(output)
