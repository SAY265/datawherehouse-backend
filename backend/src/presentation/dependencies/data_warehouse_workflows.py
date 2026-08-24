"""Composition root dành riêng cho Data Warehouse workflow."""

from dataclasses import dataclass
from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_sources.source_analysis_runner import SourceAnalysisRunner
from src.application.data_warehouse_workflows.data_warehouse_workflow_service import (
    DataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.source_analysis_runner import (
    WorkflowSourceAnalysisRunner,
)
from src.infrastructure.agents.data_warehouse_design_agent import DataWarehouseDesignAgent
from src.infrastructure.agents.requirement_analysis_agent import RequirementAnalysisAgent
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.llm.column_type_classifier import ColumnTypeClassifier
from src.infrastructure.llm.factory import get_cached_chat_model
from src.infrastructure.repositories.postgres_analytical_requirement_repository import (
    PostgresAnalyticalRequirementRepository,
)
from src.infrastructure.repositories.postgres_data_model_change_repository import (
    PostgresDataModelChangeRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import PostgresDataModelRepository
from src.infrastructure.repositories.postgres_data_source_repository import PostgresDataSourceRepository
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.repositories.postgres_requirement_repository import PostgresRequirementRepository
from src.infrastructure.security.pii_guard import PiiGuard
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.storage.source_file_inspector import SourceFileInspector
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.data_model_resources import get_pii_guard, get_validation_engine
from src.presentation.dependencies.project_access import ProjectAccessDependency


@dataclass(frozen=True, slots=True)
class _WorkflowRepositories:
    """Typed repository bundle chia sẻ cùng request-scoped session."""

    projects: PostgresProjectRepository
    requirements: PostgresRequirementRepository
    analytical: PostgresAnalyticalRequirementRepository
    data_sources: PostgresDataSourceRepository
    models: PostgresDataModelRepository
    changes: PostgresDataModelChangeRepository


def get_data_warehouse_workflow(
    access: ProjectAccessDependency,
    pii_guard: Annotated[PiiGuard, Depends(get_pii_guard)],
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataWarehouseWorkflowService:
    """Wiring workflow với Agent, typed repositories và persistence adapters."""
    repositories = _repositories(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    source_analysis = WorkflowSourceAnalysisRunner(
        repositories.data_sources,
        LocalFileStorage(get_settings().upload_dir),
        SourceAnalysisRunner(
            SourceFileInspector(),
            ColumnTypeClassifier(get_cached_chat_model, pii_guard),
        ),
        unit_of_work,
        access,
    )
    return DataWarehouseWorkflowService(
        repositories.projects,
        repositories.requirements,
        repositories.analytical,
        repositories.data_sources,
        repositories.models,
        repositories.changes,
        RequirementAnalysisAgent(get_cached_chat_model, pii_guard),
        source_analysis,
        DataWarehouseDesignAgent(get_cached_chat_model, pii_guard),
        get_validation_engine(),
        unit_of_work,
        access,
    )


def _repositories(session: AsyncSession) -> _WorkflowRepositories:
    """Khởi tạo typed repository bundle cho một workflow request."""
    return _WorkflowRepositories(
        projects=PostgresProjectRepository(session),
        requirements=PostgresRequirementRepository(session),
        analytical=PostgresAnalyticalRequirementRepository(session),
        data_sources=PostgresDataSourceRepository(session),
        models=PostgresDataModelRepository(session),
        changes=PostgresDataModelChangeRepository(session),
    )


DataWarehouseWorkflowDependency = Annotated[
    IDataWarehouseWorkflowService,
    Depends(get_data_warehouse_workflow),
]
