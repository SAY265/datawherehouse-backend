"""REST endpoints cho Analyze Changes và trạng thái outdated."""

from fastapi import APIRouter
from src.application.data_warehouse_workflows.input import (
    GetAnalysisStatusInput,
    ReanalyzeProjectInput,
)
from src.presentation.dependencies.data_warehouse_workflows import DataWarehouseWorkflowDependency
from src.presentation.dtos.data_models.request import ProjectIdPath
from src.presentation.dtos.data_warehouse_workflows.response import AnalysisStatusResponse
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}",
    tags=["Project Analysis"],
    route_class=ApiResponseRoute,
)


@router.get(
    "/analysis-status",
    response_model=AnalysisStatusResponse,
    operation_id="getProjectAnalysisStatus",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_project_analysis_status(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Đọc trạng thái outdated mà không gọi LLM."""
    output = await service.get_analysis_status(GetAnalysisStatusInput(project_id))
    return AnalysisStatusResponse.from_application(output)


@router.post(
    "/reanalyze",
    response_model=AnalysisStatusResponse,
    operation_id="reanalyzeProject",
    responses=error_responses(401, 403, 404, 409, 422, 500, 502),
)
async def reanalyze_project(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Chạy RequirementAgent cho những analysis đã outdated."""
    output = await service.reanalyze(ReanalyzeProjectInput(project_id))
    return AnalysisStatusResponse.from_application(output)

