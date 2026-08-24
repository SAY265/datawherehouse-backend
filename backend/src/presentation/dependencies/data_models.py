"""Dependency wiring dành riêng cho Data Model application service."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.project_access_guard import ProjectAccessGuard
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.i_data_model_chat_service import IDataModelChatService
from src.application.data_models.i_data_model_service import IDataModelService
from src.infrastructure.codegen.pydbml_artifact_generator import PyDbmlArtifactGenerator
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.llm.data_model_insight_analyzer import LlmDataModelInsightAnalyzer
from src.infrastructure.llm.llm_data_model_chat_service import LlmDataModelChatService
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_project_member_repository import PostgresProjectMemberRepository
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.auth import CurrentUserDependency


def get_data_model_service(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataModelService:
    """Khởi tạo Data Model service và Unit of Work dùng chung session."""
    repository = PostgresDataModelRepository(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    artifact_generator = PyDbmlArtifactGenerator()
    settings = get_settings()
    effective_api_key = settings.openrouter_api_key or settings.openai_api_key
    insight_analyzer = LlmDataModelInsightAnalyzer(
        artifact_generator,
        api_key=effective_api_key,
        base_url=settings.openai_base_url,
        model_name=settings.model_name,
        max_tokens=settings.max_tokens,
    )
    return DataModelService(
        repository,
        unit_of_work,
        artifact_generator,
        insight_analyzer,
        access_guard=ProjectAccessGuard(
            PostgresProjectRepository(session),
            PostgresProjectMemberRepository(session),
        ),
        current_user_id=current_user.id,
    )


def get_data_model_chat_service(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataModelChatService:
    """Khởi tạo Data Model AI Chatbot Service."""
    settings = get_settings()
    effective_api_key = settings.openrouter_api_key or settings.openai_api_key
    return LlmDataModelChatService(
        api_key=effective_api_key,
        base_url=settings.openai_base_url,
        model_name=settings.model_name,
        max_tokens=settings.max_tokens,
        access_guard=ProjectAccessGuard(
            PostgresProjectRepository(session),
            PostgresProjectMemberRepository(session),
        ),
        current_user_id=current_user.id,
    )


DataModelServiceDependency = Annotated[
    IDataModelService,
    Depends(get_data_model_service),
]

DataModelChatServiceDependency = Annotated[
    IDataModelChatService,
    Depends(get_data_model_chat_service),
]
