"""REST endpoints cho Data Model hiện tại của dự án."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from src.application.data_models.input import DataModelChatInput, GetDataModelInput
from src.presentation.dependencies.auth import get_current_user
from src.presentation.dependencies.data_models import (
    DataModelChatServiceDependency,
    DataModelServiceDependency,
)
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.data_models.request import (
    DataModelChatRequest,
    ProjectIdPath,
    RunRelationshipAgentRequest,
    UpdateDataModelRequest,
)
from src.presentation.dtos.data_models.response import (
    DataModelChatResponse,
    DataModelDdlResponse,
    DataModelInsightResponse,
    DataModelResponse,
    RelationshipAgentResponse,
)
from src.presentation.routing import ApiResponseRoute

router = APIRouter(
    prefix="/projects/{project_id}/data-model",
    tags=["Data Models"],
    route_class=ApiResponseRoute,
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "",
    response_model=DataModelResponse,
    operation_id="getDataModel",
    responses={
        404: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def get_current_data_model(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lấy DBML và revision hiện tại của dự án."""
    output = await service.get_data_model(GetDataModelInput(project_id=project_id))
    return DataModelResponse.from_application(output)


@router.put(
    "",
    response_model=DataModelResponse,
    operation_id="updateDataModel",
    responses={
        404: {"model": ApiErrorResponse},
        409: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def update_current_data_model(
    project_id: ProjectIdPath,
    request: UpdateDataModelRequest,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lưu snapshot DBML mới bằng optimistic locking."""
    output = await service.update_data_model(request.to_application(project_id))
    return DataModelResponse.from_application(output)


@router.get(
    "/ddl",
    response_model=DataModelDdlResponse,
    operation_id="getDataModelDdl",
)
async def get_data_model_ddl(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
    dialect: Literal["postgresql"] = Query(default="postgresql"),
) -> DataModelDdlResponse:
    """Sinh PostgreSQL DDL từ snapshot DBML hiện tại."""
    output = await service.generate_ddl(GetDataModelInput(project_id=project_id), dialect)
    return DataModelDdlResponse.from_application(output)


@router.get(
    "/insights",
    response_model=list[DataModelInsightResponse],
    operation_id="getDataModelInsights",
)
async def get_data_model_insights(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
) -> list[DataModelInsightResponse]:
    """Phân tích DBML hiện tại thành danh sách insight theo bảng."""
    outputs = await service.get_insights(GetDataModelInput(project_id=project_id))
    return [DataModelInsightResponse.from_application(item) for item in outputs]


@router.post(
    "/relationship-agent",
    response_model=RelationshipAgentResponse,
    operation_id="runDataModelRelationshipAgent",
    responses={
        403: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def run_data_model_relationship_agent(
    project_id: ProjectIdPath,
    request: RunRelationshipAgentRequest,
    service: DataModelServiceDependency,
) -> RelationshipAgentResponse:
    """Tự nối bảng trên draft và cảnh báo các bảng đích còn thiếu."""
    output = await service.run_relationship_agent(request.to_application(project_id))
    return RelationshipAgentResponse.from_application(output)


@router.post(
    "/chat",
    response_model=DataModelChatResponse,
    operation_id="chatWithDataModel",
)
async def chat_with_data_model(
    project_id: ProjectIdPath,
    request: DataModelChatRequest,
    chat_service: DataModelChatServiceDependency,
) -> DataModelChatResponse:
    """Tương tác với AI Chatbot để giải đáp thắc mắc, phân tích schema hoặc sinh bảng mới."""
    chat_input = DataModelChatInput(
        project_id=project_id,
        message=request.message,
        current_dbml=request.current_dbml,
        selected_table=request.selected_table,
        history=request.history,
    )
    output = await chat_service.chat(chat_input)
    return DataModelChatResponse.from_application(output)
