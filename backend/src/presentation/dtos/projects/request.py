"""Request DTOs cho Project Init."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.projects.input import (
    CreateProjectInput,
    LoadProjectSourceInput,
    UpdateProjectInput,
)


class SourceReferenceRequest(BaseModel):
    """Đích FK được khai báo rõ trong DDL nguồn."""

    model_config = ConfigDict(extra="forbid")

    table: str = Field(min_length=1, max_length=255)
    column: str = Field(min_length=1, max_length=200)


class SourceColumnRequest(BaseModel):
    """Metadata một cột nguồn dùng để tạo Data Model ban đầu."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1, max_length=200)
    label: str = Field(min_length=1, max_length=200)
    type: str = Field(min_length=1, max_length=50)
    is_primary_key: bool = False
    is_nullable: bool = True
    references: SourceReferenceRequest | None = None


class SourceTableRequest(BaseModel):
    """Schema một bảng nguồn; không nhận dữ liệu hàng để tránh gửi dữ liệu thô cho AI."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    columns: list[SourceColumnRequest] = Field(default_factory=list, max_length=500)


class CreateProjectRequest(BaseModel):
    """Payload khởi tạo workflow project."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255, description="Tên dự án là bắt buộc")
    domain: str = Field(min_length=1, max_length=100)
    target_dialect: Literal["postgresql"] = "postgresql"
    business_description: str = Field(default="", max_length=10_000)
    is_masking_enabled: bool = True
    source_tables: list[SourceTableRequest] = Field(default_factory=list, max_length=100)

    def to_application(self) -> CreateProjectInput:
        """Ánh xạ request sang input application."""
        return CreateProjectInput(
            name=self.name.strip(),
            domain=self.domain,
            target_dialect=self.target_dialect,
            business_description=self.business_description,
            is_masking_enabled=self.is_masking_enabled,
            source_tables=tuple(table.model_dump() for table in self.source_tables),
        )


class LoadProjectSourceRequest(BaseModel):
    """Payload nạp schema sau khi project đã được tạo."""

    model_config = ConfigDict(extra="forbid")

    target_dialect: Literal["postgresql"] = "postgresql"
    is_masking_enabled: bool = True
    source_tables: list[SourceTableRequest] = Field(min_length=1, max_length=100)

    def to_application(self, project_id: UUID) -> LoadProjectSourceInput:
        return LoadProjectSourceInput(
            project_id=project_id,
            target_dialect=self.target_dialect,
            is_masking_enabled=self.is_masking_enabled,
            source_tables=tuple(table.model_dump() for table in self.source_tables),
        )


class UpdateProjectRequest(BaseModel):
    """Payload cập nhật thông tin dự án."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10_000)
    domain: str | None = Field(default=None, min_length=1, max_length=100)
    status: str | None = Field(default=None, max_length=50)

    def to_application(self, project_id: UUID) -> UpdateProjectInput:
        """Ánh xạ request sang input application."""
        return UpdateProjectInput(
            project_id=project_id,
            name=self.name.strip() if self.name is not None else None,
            description=self.description.strip() if self.description is not None else None,
            domain=self.domain.strip() if self.domain is not None else None,
            status=self.status.strip().upper() if self.status is not None else None,
        )
