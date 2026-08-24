"""Dependency wiring cho Project application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.projects.i_project_service import IProjectService
from src.application.projects.project_service import ProjectService
from src.application.common.project_access_guard import ProjectAccessGuard
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.repositories.postgres_project_member_repository import PostgresProjectMemberRepository
from src.infrastructure.storage.session_data_manager import get_session_data_manager
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_project_service(
    session: AsyncSession = Depends(get_async_db_session),
) -> IProjectService:
    """Khởi tạo Project service với cùng một transaction."""
    project_repository = PostgresProjectRepository(session)
    return ProjectService(
        project_repository=project_repository,
        data_model_repository=PostgresDataModelRepository(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        session_data_manager=get_session_data_manager(),
        access_guard=ProjectAccessGuard(
            project_repository,
            PostgresProjectMemberRepository(session),
        ),
    )


ProjectServiceDependency = Annotated[IProjectService, Depends(get_project_service)]
