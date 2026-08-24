"""Persist full CSV analysis cho các Data Source đang pending."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_sources.i_data_source_service import IDataSourceFileStore
from src.application.data_sources.source_analysis_models import SourceFileAnalysisInput
from src.application.data_sources.source_analysis_runner import SourceAnalysisRunner
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.entities import DataSource
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.entities import Project


class WorkflowSourceAnalysisRunner:
    """Đọc file pending, phân tích ngoài transaction và persist atomically."""

    def __init__(
        self,
        sources: IDataSourceRepository,
        files: IDataSourceFileStore,
        analyzer: SourceAnalysisRunner,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
    ) -> None:
        self._sources = sources
        self._files = files
        self._analyzer = analyzer
        self._unit_of_work = unit_of_work
        self._access = access

    async def analyze_pending(self, project: Project) -> None:
        """Phân tích source chưa có schema và chặn persist kết quả stale."""
        sources = await self._sources.list_by_project(project.id)
        pending = tuple(source for source in sources if source.schema_metadata is None)
        if not pending:
            return
        await self._unit_of_work.rollback()
        inputs = await self._read_inputs(pending)
        analyzed = await self._analyzer.analyze(inputs)
        async with self._unit_of_work:
            current = await self._access.require_owner(project.id)
            _ensure_source_revision(current.source_revision, project.source_revision)
            persisted = {item.id: item for item in await self._sources.list_by_project(project.id)}
            for result in analyzed:
                source = persisted[result.source_id]
                source.replace_file(source.location, result.schema_metadata)
                await self._sources.save(source)
            await self._unit_of_work.commit()

    async def _read_inputs(
        self,
        sources: tuple[DataSource, ...],
    ) -> tuple[SourceFileAnalysisInput, ...]:
        inputs = []
        for source in sources:
            content = await self._files.read_file(source.location)
            inputs.append(SourceFileAnalysisInput(source.id, source.name, content))
        return tuple(inputs)


def _ensure_source_revision(current: int, expected: int) -> None:
    if current != expected:
        raise BusinessException(
            ErrorCode.ANALYSIS_INPUT_CHANGED,
            "Nguồn dữ liệu đã thay đổi trong lúc phân tích.",
        )
