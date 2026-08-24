"""Dependency wiring dành riêng cho Requirement application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.requirement_service import RequirementService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_requirement_service(
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IRequirementService:
    """Khởi tạo Requirement service và Unit of Work dùng chung session."""
    return RequirementService(
        requirements=PostgresRequirementRepository(session),
        access=access,
    )


RequirementServiceDependency = Annotated[
    IRequirementService,
    Depends(get_requirement_service),
]
