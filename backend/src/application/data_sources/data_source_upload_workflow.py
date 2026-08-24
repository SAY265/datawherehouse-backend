"""Transactional batch upload workflow for tabular data sources."""

from dataclasses import dataclass

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_sources.data_source_upload_policy import validate_upload
from src.application.data_sources.file_mutation_log import FileMutationLog, FileReplacement
from src.application.data_sources.i_data_source_service import IDataSourceFileStore
from src.application.data_sources.input import UploadDataSourcesInput, UploadFileInput
from src.application.data_sources.output import DataSourceOutput, UploadDataSourcesOutput
from src.application.data_sources.source_analysis_ports import ISourceFileInspector
from src.domain.data_source.entities import DataSource
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class _SourceSaveInput:
    project_id: EntityID
    file: UploadFileInput
    existing: DataSource | None
    mutations: FileMutationLog


class DataSourceUploadWorkflow:
    """Validates a whole batch, then coordinates DB and reversible file writes."""

    def __init__(
        self,
        sources: IDataSourceRepository,
        files: IDataSourceFileStore,
        inspector: ISourceFileInspector,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        projects: IProjectRepository,
    ) -> None:
        self._sources = sources
        self._files = files
        self._inspector = inspector
        self._unit_of_work = unit_of_work
        self._access = access
        self._projects = projects

    async def execute(self, data: UploadDataSourcesInput) -> UploadDataSourcesOutput:
        """Upload a validated batch and compensate files when the UoW fails."""
        mutations = FileMutationLog(self._files)
        try:
            async with self._unit_of_work:
                project = await self._access.require_owner(data.project_id)
                existing = await self._sources.list_by_project(data.project_id)
                by_name = {source.name.casefold(): source for source in existing}
                validate_upload(data, frozenset(by_name))
                self._validate_all(data)
                uploaded = await self._process_all(data, by_name, mutations)
                project.increment_source_revision()
                await self._projects.save(project)
                await self._unit_of_work.commit()
        except Exception:
            await mutations.rollback()
            raise
        return UploadDataSourcesOutput(tuple(uploaded), len(data.files))

    def _validate_all(self, data: UploadDataSourcesInput) -> None:
        for item in data.files:
            self._inspector.validate(item.content, item.filename)

    async def _process_all(
        self,
        data: UploadDataSourcesInput,
        existing: dict[str, DataSource],
        mutations: FileMutationLog,
    ) -> list[DataSourceOutput]:
        uploaded = []
        for item in data.files:
            key = item.filename.casefold()
            saved = await self._save_source(
                _SourceSaveInput(data.project_id, item, existing.get(key), mutations)
            )
            existing[key] = saved
            uploaded.append(DataSourceOutput.from_domain(saved))
        return uploaded

    async def _save_source(self, data: _SourceSaveInput) -> DataSource:
        file = data.file
        location = await data.mutations.replace(
            FileReplacement(
                str(data.project_id),
                file.filename,
                file.content,
                data.existing.location if data.existing else None,
            )
        )
        source = data.existing or DataSource(
            project_id=data.project_id,
            name=file.filename,
            location=location,
            type=self._inspector.source_type(file.filename),
        )
        source.type = self._inspector.source_type(file.filename)
        source.replace_file(location, None)
        return await self._sources.save(source)
