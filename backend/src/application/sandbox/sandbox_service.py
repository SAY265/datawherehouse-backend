"""Application service chứa trọn các use case của Sandbox module."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.sandbox.i_sandbox_service import (
    ISandboxExecutor,
    ISandboxService,
)
from src.application.sandbox.input import (
    ExecuteSandboxDdlInput,
    GetSandboxConfigInput,
    SaveSandboxConfigInput,
    TestSandboxConnectionInput,
)
from src.application.sandbox.output import (
    ConnectionTestOutput,
    SandboxConfigOutput,
    SandboxExecutionOutput,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.uuid import generate_uuid
from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.i_sandbox_config_repository import ISandboxConfigRepository
from typing_extensions import override


class SandboxService(ISandboxService):
    """Điều phối config, authorization và Sandbox executor."""

    def __init__(
        self,
        configs: ISandboxConfigRepository,
        unit_of_work: IUnitOfWork,
        executor: ISandboxExecutor,
        access: ProjectAccessPolicy,
    ) -> None:
        self._configs = configs
        self._unit_of_work = unit_of_work
        self._executor = executor
        self._access = access

    @override
    async def get_config(self, data: GetSandboxConfigInput) -> SandboxConfigOutput | None:
        await self._access.require_member(data.project_id)
        config = await self._configs.get_by_project_id(data.project_id)
        return SandboxConfigOutput.from_domain(config) if config else None

    @override
    async def save_config(self, data: SaveSandboxConfigInput) -> SandboxConfigOutput:
        async with self._unit_of_work:
            await self._access.require_owner(data.project_id)
            existing = await self._configs.get_by_project_id(data.project_id)
            config = _build_config(data, existing)
            saved = await self._configs.save(config)
            await self._unit_of_work.commit()
        return SandboxConfigOutput.from_domain(saved)

    @override
    async def test_connection(self, data: TestSandboxConnectionInput) -> ConnectionTestOutput:
        await self._access.require_owner(data.project_id)
        return await self._executor.test_connection(data.connection)

    @override
    async def execute_ddl(self, data: ExecuteSandboxDdlInput) -> SandboxExecutionOutput:
        async with self._unit_of_work:
            await self._access.require_owner(data.project_id)
            config = await self._configs.get_by_project_id(data.project_id)
            if config is None:
                raise BusinessException(
                    code=ErrorCode.SANDBOX_CONFIG_NOT_FOUND,
                    message="Dự án chưa có cấu hình Sandbox.",
                )
            return await self._executor.execute(config, data.ddl_script, data.reset_schema)


def _build_config(
    data: SaveSandboxConfigInput,
    existing: SandboxConfig | None,
) -> SandboxConfig:
    connection = data.connection
    return SandboxConfig(
        id=existing.id if existing else generate_uuid(),
        project_id=data.project_id,
        db_type=connection.db_type,
        host=connection.host,
        port=connection.port,
        database_name=connection.database_name,
        username=connection.username,
        password=connection.password or (existing.password if existing else None),
        schema_name=connection.schema_name,
    )
