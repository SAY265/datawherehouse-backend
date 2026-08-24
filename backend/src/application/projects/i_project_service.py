"""Interface duy nhất của module Project."""

from abc import ABC, abstractmethod

from src.application.data_models.output import DataModelOutput
from src.application.projects.input import (
    CreateProjectInput,
    LoadProjectSourceInput,
    UpdateProjectInput,
)
from src.application.projects.output import (
    ProjectDetailOutput,
    ProjectOutput,
    ProjectSummaryOutput,
)
from src.domain.shared.types import EntityID


class IProjectService(ABC):
    """Hợp đồng application cho các use case Project."""

    @abstractmethod
    async def create_project(self, data: CreateProjectInput, user_id: EntityID) -> ProjectOutput:
        """Tạo project và Data Model snapshot ban đầu."""
        raise NotImplementedError

    @abstractmethod
    async def list_projects(self, user_id: EntityID) -> list[ProjectSummaryOutput]:
        """List projects owned by the authenticated user."""
        raise NotImplementedError

    @abstractmethod
    async def get_project(self, project_id: EntityID, user_id: EntityID) -> ProjectDetailOutput:
        """Lấy chi tiết dự án thuộc sở hữu của user."""
        raise NotImplementedError

    @abstractmethod
    async def update_project(
        self, data: UpdateProjectInput, user_id: EntityID
    ) -> ProjectDetailOutput:
        """Cập nhật thông tin dự án (tên, lĩnh vực, mô tả)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_project(self, project_id: EntityID, user_id: EntityID) -> bool:
        """Xóa dự án và các tài nguyên phụ thuộc."""
        raise NotImplementedError

    @abstractmethod
    async def load_source_schema(
        self, data: LoadProjectSourceInput, user_id: EntityID
    ) -> DataModelOutput:
        """Nạp schema nguồn vào project đã được tạo và thay snapshot khởi tạo."""
        raise NotImplementedError
