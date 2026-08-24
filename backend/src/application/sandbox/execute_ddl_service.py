"""Triển khai Service Thực thi DDL Sandbox (UC9.2)."""

from uuid import UUID

from src.application.common.project_access_guard import ProjectAccessGuard
from src.application.sandbox.dto import ExecuteDdlRequest, ExecuteDdlResponse, StatementLogDto
from src.application.sandbox.i_execute_ddl_service import IExecuteDdlService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.sandbox.repository import ISandboxConfigRepository
from src.domain.shared.types import EntityID
from src.infrastructure.sandbox.sandbox_executor import execute_sandbox_ddl
from typing_extensions import override


class ExecuteDdlService(IExecuteDdlService):
    """Service thực thi mã DDL script trên Sandbox Database."""

    def __init__(
        self,
        repository: ISandboxConfigRepository,
        access_guard: ProjectAccessGuard | None = None,
        current_user_id: EntityID | None = None,
    ) -> None:
        """Khởi tạo service với repository cấu hình Sandbox."""
        self._repository: ISandboxConfigRepository = repository
        self._access_guard = access_guard
        self._current_user_id = current_user_id

    @override
    async def execute_ddl(self, project_id: UUID, request: ExecuteDdlRequest) -> ExecuteDdlResponse:
        """Thực thi DDL chỉ khi user có quyền và project đã cấu hình Sandbox."""
        if self._access_guard is not None and self._current_user_id is not None:
            await self._access_guard.verify_project_access(project_id, self._current_user_id)
        config = await self._repository.get_by_project_id(project_id)
        if not config:
            raise BusinessException(
                code=ErrorCode.SANDBOX_CONFIG_NOT_FOUND,
                message="Dự án chưa có cấu hình Sandbox.",
            )

        result = await execute_sandbox_ddl(config, request.ddl_script)

        log_dtos = [
            StatementLogDto(
                statement=log.statement,
                is_success=log.is_success,
                execution_time_ms=log.execution_time_ms,
                timestamp=log.timestamp,
                error_detail=log.error_detail,
            )
            for log in result.logs
        ]

        return ExecuteDdlResponse(
            success=result.success,
            executed_statements=result.executed_statements,
            succeeded_statements=result.succeeded_statements,
            failed_statements=result.failed_statements,
            total_duration_ms=result.total_duration_ms,
            logs=log_dtos,
        )
