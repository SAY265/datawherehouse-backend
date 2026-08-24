"""Module chứa các triển khai PostgreSQL Repository cho tầng Infrastructure."""

from src.infrastructure.repositories.postgres_agent_session_repository import PostgresAgentSessionRepository
from src.infrastructure.repositories.postgres_analytical_requirement_repository import (
    PostgresAnalyticalRequirementRepository,
)
from src.infrastructure.repositories.postgres_data_model_change_repository import (
    PostgresDataModelChangeRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import PostgresDataModelRepository
from src.infrastructure.repositories.postgres_data_source_repository import PostgresDataSourceRepository
from src.infrastructure.repositories.postgres_project_member_repository import (
    PostgresProjectMemberRepository,
)
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.repositories.postgres_requirement_repository import PostgresRequirementRepository
from src.infrastructure.repositories.postgres_session_event_repository import (
    PostgresSessionEventRepository,
)
from src.infrastructure.repositories.postgres_user_repository import PostgresUserRepository

__all__: list[str] = [
    "PostgresUserRepository",
    "PostgresProjectRepository",
    "PostgresProjectMemberRepository",
    "PostgresRequirementRepository",
    "PostgresAnalyticalRequirementRepository",
    "PostgresDataSourceRepository",
    "PostgresAgentSessionRepository",
    "PostgresSessionEventRepository",
    "PostgresDataModelRepository",
    "PostgresDataModelChangeRepository",
]
