"""Composition root cho Project Session service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.project_sessions.i_project_session_service import IProjectSessionService
from src.application.project_sessions.project_session_service import (
    ProjectSessionDependencies,
    ProjectSessionService,
)
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_project_session_repository import PostgresProjectSessionRepository
from src.infrastructure.repositories.postgres_session_event_repository import PostgresSessionEventRepository
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.data_warehouse_workflows import DataWarehouseWorkflowDependency
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_project_session_service(
    workflow: DataWarehouseWorkflowDependency,
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IProjectSessionService:
    """Nối repositories và workflow bằng cùng request-scoped session."""
    return ProjectSessionService(
        ProjectSessionDependencies(
            PostgresProjectSessionRepository(session),
            PostgresSessionEventRepository(session),
            workflow,
            SqlAlchemyUnitOfWork(session),
            access,
        )
    )


ProjectSessionServiceDependency = Annotated[
    IProjectSessionService,
    Depends(get_project_session_service),
]
