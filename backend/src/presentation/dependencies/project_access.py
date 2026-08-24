"""Dependency dùng chung cho authorization theo Project."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_project_member_repository import (
    PostgresProjectMemberRepository,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.presentation.dependencies.auth import CurrentUserDependency


def get_project_access_policy(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> ProjectAccessPolicy:
    """Dựng policy request-scoped từ actor và database session hiện hành."""
    return ProjectAccessPolicy(
        PostgresProjectRepository(session),
        PostgresProjectMemberRepository(session),
        current_user.id,
    )


ProjectAccessDependency = Annotated[
    ProjectAccessPolicy,
    Depends(get_project_access_policy),
]
