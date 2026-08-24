"""Dependency injection cho các dịch vụ thuộc Sandbox."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.project_access_guard import ProjectAccessGuard
from src.application.sandbox.ai_ddl_fixer_service import AiDdlFixerService
from src.application.sandbox.execute_ddl_service import ExecuteDdlService
from src.application.sandbox.i_execute_ddl_service import IExecuteDdlService
from src.application.sandbox.i_sandbox_config_service import ISandboxConfigService
from src.application.sandbox.sandbox_config_service import SandboxConfigService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_project_member_repository import PostgresProjectMemberRepository
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.repositories.postgres_sandbox_config_repository import (
    PostgresSandboxConfigRepository,
)
from src.infrastructure.security.credential_cipher import CredentialCipher
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.auth import CurrentUserDependency


def _repository(session: AsyncSession) -> PostgresSandboxConfigRepository:
    """Tạo repository có cipher dùng application secret hiện hành."""
    return PostgresSandboxConfigRepository(
        session,
        CredentialCipher(get_settings().secret_key),
    )


def get_sandbox_config_service(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> ISandboxConfigService:
    """Khởi tạo service quản lý cấu hình Sandbox."""
    repository = _repository(session)
    return SandboxConfigService(
        repository,
        SqlAlchemyUnitOfWork(session),
        ProjectAccessGuard(PostgresProjectRepository(session), PostgresProjectMemberRepository(session)),
        current_user.id,
    )


def get_execute_ddl_service(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IExecuteDdlService:
    """Khởi tạo service thực thi DDL Sandbox."""
    repository = _repository(session)
    return ExecuteDdlService(
        repository,
        ProjectAccessGuard(PostgresProjectRepository(session), PostgresProjectMemberRepository(session)),
        current_user.id,
    )


def get_ai_ddl_fixer_service() -> AiDdlFixerService:
    """Khởi tạo service AI sửa lỗi DDL."""
    return AiDdlFixerService()


SandboxConfigServiceDependency = Annotated[
    ISandboxConfigService,
    Depends(get_sandbox_config_service),
]

ExecuteDdlServiceDependency = Annotated[
    IExecuteDdlService,
    Depends(get_execute_ddl_service),
]

AiDdlFixerServiceDependency = Annotated[
    AiDdlFixerService,
    Depends(get_ai_ddl_fixer_service),
]
