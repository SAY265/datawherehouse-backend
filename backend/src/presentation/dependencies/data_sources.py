"""Dependency wiring cho Data Source application service."""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_sources.data_source_service import DataSourceService
from src.application.data_sources.i_data_source_service import IDataSourceService
from src.application.data_sources.input import DataSourceColumnTargetInput
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_source_repository import PostgresDataSourceRepository
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.storage.source_file_inspector import SourceFileInspector
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.project_access import ProjectAccessDependency
from src.presentation.dtos.data_sources.request import (
    ColumnNamePath,
    ProjectIdPath,
    SourceIdPath,
    TableNamePath,
)


def get_data_source_service(
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataSourceService:
    """Khởi tạo service với actor và transaction của request hiện tại."""
    projects = PostgresProjectRepository(session)
    return DataSourceService(
        sources=PostgresDataSourceRepository(session),
        files=LocalFileStorage(get_settings().upload_dir),
        inspector=SourceFileInspector(),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        access=access,
        projects=projects,
    )


DataSourceServiceDependency = Annotated[
    IDataSourceService,
    Depends(get_data_source_service),
]


@dataclass(frozen=True, slots=True)
class DataSourcePathContext:
    """Project và Data Source lấy từ path."""

    project_id: UUID
    source_id: UUID


@dataclass(frozen=True, slots=True)
class ColumnPathContext:
    """Tên bảng và cột lấy từ path."""

    table_name: str
    column_name: str


def get_data_source_path(
    project_id: ProjectIdPath,
    source_id: SourceIdPath,
) -> DataSourcePathContext:
    """Gom định danh Project/Data Source thành context."""
    return DataSourcePathContext(project_id, source_id)


def get_column_path(
    table_name: TableNamePath,
    column_name: ColumnNamePath,
) -> ColumnPathContext:
    """Gom định danh table/column thành context."""
    return ColumnPathContext(table_name, column_name)


def get_data_source_column_context(
    source: Annotated[DataSourcePathContext, Depends(get_data_source_path)],
    column: Annotated[ColumnPathContext, Depends(get_column_path)],
    service: DataSourceServiceDependency,
) -> tuple[DataSourceColumnTargetInput, IDataSourceService]:
    """Ghép path target với application service."""
    target = DataSourceColumnTargetInput(
        project_id=source.project_id,
        data_source_id=source.source_id,
        table_name=column.table_name,
        column_name=column.column_name,
    )
    return target, service


DataSourceColumnContextDependency = Annotated[
    tuple[DataSourceColumnTargetInput, IDataSourceService],
    Depends(get_data_source_column_context),
]
