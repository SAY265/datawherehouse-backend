"""REST endpoints cho Quản lý Sandbox và Chạy thử DDL."""

from uuid import UUID

from fastapi import APIRouter, Depends, Path
from src.application.sandbox.dto import (
    ExecuteDdlRequest,
    ExecuteDdlResponse,
    FixDdlWithAiRequest,
    FixDdlWithAiResponse,
    SandboxConfigRequest,
    SandboxConfigResponse,
    TestConnectionRequest,
    TestConnectionResponse,
)
from src.presentation.dependencies.auth import get_current_user
from src.presentation.dependencies.sandbox import (
    AiDdlFixerServiceDependency,
    ExecuteDdlServiceDependency,
    SandboxConfigServiceDependency,
)
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.routing import ApiResponseRoute

router = APIRouter(
    prefix="",
    tags=["Sandbox"],
    route_class=ApiResponseRoute,
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/projects/{project_id}/sandbox/config",
    response_model=SandboxConfigResponse | None,
    operation_id="getSandboxConfig",
    responses={
        404: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def get_sandbox_config(
    project_id: UUID = Path(..., description="ID dự án"),
    service: SandboxConfigServiceDependency = None,
) -> SandboxConfigResponse | None:
    """Lấy cấu hình Sandbox DB của dự án."""
    return await service.get_config(project_id)


@router.post(
    "/projects/{project_id}/sandbox/config",
    response_model=SandboxConfigResponse,
    operation_id="saveSandboxConfig",
    responses={
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def save_sandbox_config(
    request: SandboxConfigRequest,
    project_id: UUID = Path(..., description="ID dự án"),
    service: SandboxConfigServiceDependency = None,
) -> SandboxConfigResponse:
    """Lưu hoặc cập nhật thông tin cấu hình Sandbox DB cho dự án."""
    return await service.save_config(project_id, request)


@router.post(
    "/projects/{project_id}/sandbox/test-connection",
    response_model=TestConnectionResponse,
    operation_id="testSandboxConnection",
    responses={
        400: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def test_sandbox_connection_endpoint(
    request: TestConnectionRequest,
    project_id: UUID = Path(..., description="ID dự án"),
    service: SandboxConfigServiceDependency = None,
) -> TestConnectionResponse:
    """Kiểm tra thử kết nối đến cơ sở dữ liệu Sandbox."""
    return await service.test_connection(project_id, request)


@router.post(
    "/projects/{project_id}/sandbox/execute-ddl",
    response_model=ExecuteDdlResponse,
    operation_id="executeSandboxDdl",
    responses={
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def execute_sandbox_ddl_endpoint(
    request: ExecuteDdlRequest,
    project_id: UUID = Path(..., description="ID dự án"),
    service: ExecuteDdlServiceDependency = None,
) -> ExecuteDdlResponse:
    """Thực thi mã DDL script trên Sandbox Database đã cấu hình của dự án."""
    return await service.execute_ddl(project_id, request)


@router.post(
    "/projects/{project_id}/sandbox/fix-ddl",
    response_model=FixDdlWithAiResponse,
    operation_id="fixSandboxDdlWithAi",
    responses={
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
@router.post(
    "/sandbox/fix-ddl",
    response_model=FixDdlWithAiResponse,
    operation_id="fixDdlWithAiDirect",
    responses={
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def fix_sandbox_ddl_with_ai_endpoint(
    request: FixDdlWithAiRequest,
    project_id: UUID | None = None,
    service: AiDdlFixerServiceDependency = None,
) -> FixDdlWithAiResponse:
    """Tự động phân tích lỗi và sửa mã DDL bằng AI."""
    return await service.fix_ddl(request)
