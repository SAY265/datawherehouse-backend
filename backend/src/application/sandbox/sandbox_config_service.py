"""Triển khai Service Quản lý Cấu hình Sandbox (UC9.1)."""

from uuid import UUID

from src.application.common.project_access_guard import ProjectAccessGuard
from src.application.common.unit_of_work import IUnitOfWork
from src.application.sandbox.dto import (
    SandboxConfigRequest,
    SandboxConfigResponse,
    TestConnectionRequest,
    TestConnectionResponse,
)
from src.application.sandbox.i_sandbox_config_service import ISandboxConfigService
from src.domain.sandbox.repository import ISandboxConfigRepository
from src.domain.sandbox.sandbox import SandboxConfig
from src.domain.shared.types import EntityID
from src.infrastructure.sandbox.sandbox_executor import check_sandbox_connection
from typing_extensions import override


class SandboxConfigService(ISandboxConfigService):
    """Service thực thi quản lý và kiểm tra kết nối CSDL Sandbox."""

    def __init__(
        self,
        repository: ISandboxConfigRepository,
        unit_of_work: IUnitOfWork,
        access_guard: ProjectAccessGuard | None = None,
        current_user_id: EntityID | None = None,
    ) -> None:
        """Khởi tạo service với repository."""
        self._repository: ISandboxConfigRepository = repository
        self._unit_of_work = unit_of_work
        self._access_guard = access_guard
        self._current_user_id = current_user_id

    @override
    async def get_config(self, project_id: UUID) -> SandboxConfigResponse | None:
        """Lấy cấu hình Sandbox mà không tạo dữ liệu trong GET."""
        await self._authorize(project_id)
        config = await self._repository.get_by_project_id(project_id)
        if not config:
            return None

        return SandboxConfigResponse(
            id=config.id,
            project_id=config.project_id,
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            database_name=config.database_name,
            username=config.username,
            schema_name=config.schema_name,
            status="CONFIGURED",
        )

    @override
    async def save_config(self, project_id: UUID, request: SandboxConfigRequest) -> SandboxConfigResponse:
        """Lưu hoặc cập nhật cấu hình Sandbox cho dự án."""
        await self._authorize(project_id)
        existing = await self._repository.get_by_project_id(project_id)

        config = SandboxConfig(
            id=existing.id if existing else SandboxConfig(project_id=project_id).id,
            project_id=project_id,
            db_type=request.db_type,
            host=request.host,
            port=request.port,
            database_name=request.database_name,
            username=request.username,
            password=request.password or (existing.password if existing else None),
            schema_name=request.schema_name,
        )
        saved = await self._repository.save(config)
        await self._unit_of_work.commit()

        return SandboxConfigResponse(
            id=saved.id,
            project_id=saved.project_id,
            db_type=saved.db_type,
            host=saved.host,
            port=saved.port,
            database_name=saved.database_name,
            username=saved.username,
            schema_name=saved.schema_name,
            status="CONFIGURED",
        )

    @override
    async def test_connection(
        self,
        project_id: UUID,
        request: TestConnectionRequest,
    ) -> TestConnectionResponse:
        """Thử kết nối đến cơ sở dữ liệu Sandbox."""
        await self._authorize(project_id)
        success, message, latency = await check_sandbox_connection(request)
        return TestConnectionResponse(
            success=success,
            message=message,
            latency_ms=latency,
        )

    async def _authorize(self, project_id: EntityID) -> None:
        if self._access_guard is not None and self._current_user_id is not None:
            await self._access_guard.verify_project_access(project_id, self._current_user_id)
