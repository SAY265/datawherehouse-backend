"""REST endpoints cho Project Init."""

from fastapi import APIRouter
from src.presentation.dependencies.auth import CurrentUserDependency
from src.presentation.dependencies.projects import ProjectServiceDependency
from src.presentation.dtos.projects.request import (
    CreateProjectRequest,
    LoadProjectSourceRequest,
    UpdateProjectRequest,
)
from src.presentation.dtos.projects.response import (
    ProjectDetailResponse,
    ProjectResponse,
    ProjectSummaryResponse,
)
from src.presentation.dtos.data_models.response import DataModelResponse
from src.presentation.dtos.data_models.request import ProjectIdPath
from src.presentation.routing import ApiResponseRoute

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    route_class=ApiResponseRoute,
)


@router.get("", response_model=list[ProjectSummaryResponse], operation_id="listProjects")
async def list_projects(
    service: ProjectServiceDependency,
    current_user: CurrentUserDependency,
) -> list[ProjectSummaryResponse]:
    projects = await service.list_projects(current_user.id)
    return [ProjectSummaryResponse.from_application(project) for project in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    operation_id="getProject",
)
async def get_project(
    project_id: ProjectIdPath,
    service: ProjectServiceDependency,
    current_user: CurrentUserDependency,
) -> ProjectDetailResponse:
    """Lấy thông tin chi tiết một dự án."""
    output = await service.get_project(project_id, current_user.id)
    return ProjectDetailResponse.from_application(output)


@router.patch(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    operation_id="updateProject",
)
async def update_project(
    project_id: ProjectIdPath,
    request: UpdateProjectRequest,
    service: ProjectServiceDependency,
    current_user: CurrentUserDependency,
) -> ProjectDetailResponse:
    """Cập nhật tên, lĩnh vực hoặc mô tả dự án."""
    output = await service.update_project(
        request.to_application(project_id), current_user.id
    )
    return ProjectDetailResponse.from_application(output)


@router.delete(
    "/{project_id}",
    response_model=dict[str, str],
    operation_id="deleteProject",
)
async def delete_project(
    project_id: ProjectIdPath,
    service: ProjectServiceDependency,
    current_user: CurrentUserDependency,
) -> dict[str, str]:
    """Xóa một dự án và các tài nguyên liên quan."""
    await service.delete_project(project_id, current_user.id)
    return {"message": "Dự án đã được xóa thành công."}


@router.post("/init", response_model=ProjectResponse, operation_id="createProject")
async def create_project(
    request: CreateProjectRequest,
    service: ProjectServiceDependency,
    current_user: CurrentUserDependency,
) -> ProjectResponse:
    """Tạo project cùng Data Model snapshot ban đầu."""
    output = await service.create_project(request.to_application(), current_user.id)
    return ProjectResponse.from_application(output)


@router.post(
    "/{project_id}/source-schema",
    response_model=DataModelResponse,
    operation_id="loadProjectSourceSchema",
)
async def load_project_source_schema(
    project_id: ProjectIdPath,
    request: LoadProjectSourceRequest,
    service: ProjectServiceDependency,
    current_user: CurrentUserDependency,
) -> DataModelResponse:
    """Nạp schema nguồn vào một project đã tồn tại và sinh lại ERD."""
    output = await service.load_source_schema(
        request.to_application(project_id), current_user.id
    )
    return DataModelResponse.from_application(output)
