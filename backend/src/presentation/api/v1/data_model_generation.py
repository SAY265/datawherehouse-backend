"""REST endpoints cho initial design và proposal bằng Agent."""

from fastapi import APIRouter
from src.application.data_warehouse_workflows.input import (
    CreateAiEditProposalInput,
    GenerateDataModelInput,
    RegenerateDataModelInput,
)
from src.presentation.dependencies.data_warehouse_workflows import DataWarehouseWorkflowDependency
from src.presentation.dtos.data_model_changes.response import (
    ChangeProposalDetailResponse,
)
from src.presentation.dtos.data_models.request import ProjectIdPath, ReviseDataModelRequest
from src.presentation.dtos.data_models.response import DataModelResponse
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}/data-model",
    tags=["Data Models"],
    route_class=ApiResponseRoute,
)


@router.post(
    "/generate",
    response_model=DataModelResponse,
    operation_id="generateDataModel",
    responses=error_responses(401, 403, 404, 409, 422, 500, 502),
)
async def generate_data_model(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> DataModelResponse:
    """Chạy Save & Analyze và chỉ tạo Data Model đầu tiên."""
    output = await service.generate_data_model(GenerateDataModelInput(project_id))
    return DataModelResponse.from_application(output)


@router.post(
    "/regenerate",
    response_model=DataModelResponse,
    operation_id="regenerateDataModel",
    responses=error_responses(401, 403, 404, 409, 422, 500, 502),
)
async def regenerate_data_model(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> DataModelResponse:
    """Sinh lại, validate và ghi đè trực tiếp Data Model hiện hành."""
    output = await service.regenerate_data_model(RegenerateDataModelInput(project_id))
    return DataModelResponse.from_application(output)


@router.post(
    "/proposals/ai-edit",
    response_model=ChangeProposalDetailResponse,
    operation_id="createAiDataModelProposal",
    responses=error_responses(401, 403, 404, 409, 422, 500, 502),
)
async def revise_data_model_with_ai(
    project_id: ProjectIdPath,
    request: ReviseDataModelRequest,
    service: DataWarehouseWorkflowDependency,
) -> ChangeProposalDetailResponse:
    """Tạo Human Review proposal từ instruction và full project context."""
    command = CreateAiEditProposalInput(project_id, request.instruction)
    result = await service.create_ai_edit_proposal(command)
    return ChangeProposalDetailResponse.from_application(result)

