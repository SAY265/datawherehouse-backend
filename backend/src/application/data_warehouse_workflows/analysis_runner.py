"""Điều phối hai operation độc lập của RequirementAgent."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.analysis_helpers import (
    ensure_revision,
    to_requirement_context,
)
from src.application.data_warehouse_workflows.generated_entity_mapper import (
    map_generated_analytical,
    map_generated_requirements,
)
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IRequirementAnalysisAgent,
)
from src.application.data_warehouse_workflows.input import (
    AnalyticalAnalysisInput,
    RawRequirementAnalysisInput,
)
from src.application.data_warehouse_workflows.output import (
    GeneratedAnalyticalRequirement,
    GeneratedRequirement,
)
from src.application.data_warehouse_workflows.source_analysis_runner import (
    WorkflowSourceAnalysisRunner,
)
from src.application.data_warehouse_workflows.workflow_data_loader import WorkflowDataReader
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.project.entities import Project
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from src.domain.shared.types import EntityID


class WorkflowAnalysisRunner:
    """Chạy analysis cần thiết và không giữ transaction khi gọi LLM."""

    def __init__(
        self,
        projects: IProjectRepository,
        requirements: IRequirementRepository,
        analytical: IAnalyticalRequirementRepository,
        requirement_agent: IRequirementAnalysisAgent,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        reader: WorkflowDataReader,
        source_analysis: WorkflowSourceAnalysisRunner,
    ) -> None:
        self._projects = projects
        self._requirements = requirements
        self._analytical = analytical
        self._requirement_agent = requirement_agent
        self._unit_of_work = unit_of_work
        self._access = access
        self._reader = reader
        self._source_analysis = source_analysis

    async def run(self, project_id: EntityID) -> Project:
        """Phân tích các revision outdated theo đúng dependency order."""
        project = await self._access.require_owner(project_id)
        await self._source_analysis.analyze_pending(project)
        project = await self._access.require_owner(project_id)
        requirement_analyzed = await self._analyze_requirement(project)
        project = await self._access.require_owner(project_id)
        await self._analyze_sources(project, requirement_analyzed)
        return await self._access.require_owner(project_id)

    async def _analyze_requirement(self, project: Project) -> bool:
        if not project.is_requirement_analysis_outdated():
            return False
        raw_requirement = (project.requirement or "").strip()
        generated: tuple[GeneratedRequirement, ...] = ()
        if raw_requirement:
            await self._unit_of_work.rollback()
            generated = await self._requirement_agent.structure_raw_requirement(
                RawRequirementAnalysisInput(raw_requirement)
            )
        await self._save_requirements(project.id, project.requirement_revision, generated)
        return True

    async def _save_requirements(
        self,
        project_id: EntityID,
        expected_revision: int,
        generated: tuple[GeneratedRequirement, ...],
    ) -> None:
        async with self._unit_of_work:
            project = await self._access.require_owner(project_id)
            ensure_revision(project.requirement_revision, expected_revision)
            if (project.requirement or "").strip():
                entities = map_generated_requirements(project.id, generated)
                await self._requirements.replace_by_project(project.id, entities)
            await self._unit_of_work.commit()

    async def _analyze_sources(self, project: Project, requirement_analyzed: bool) -> None:
        if not requirement_analyzed and not project.is_source_analysis_outdated():
            return
        data = await self._reader.load_design_input(project.id)
        generated: tuple[GeneratedAnalyticalRequirement, ...] = ()
        if data.requirements:
            await self._unit_of_work.rollback()
            inputs = tuple(to_requirement_context(item) for item in data.requirements)
            generated = await self._requirement_agent.derive_analytical_requirements(
                AnalyticalAnalysisInput(inputs, data.data_sources)
            )
        expected_revisions = (project.requirement_revision, project.source_revision)
        await self._save_analytical(project.id, expected_revisions, generated)

    async def _save_analytical(
        self,
        project_id: EntityID,
        expected_revisions: tuple[int, int],
        generated: tuple[GeneratedAnalyticalRequirement, ...],
    ) -> None:
        async with self._unit_of_work:
            project = await self._access.require_owner(project_id)
            ensure_revision(project.requirement_revision, expected_revisions[0])
            ensure_revision(project.source_revision, expected_revisions[1])
            data = await self._reader.load_design_input(project.id)
            valid_ids = {item.id for item in data.requirements}
            entities = map_generated_analytical(generated, valid_ids)
            await self._analytical.replace_by_project(project.id, entities)
            if project.is_requirement_analysis_outdated():
                project.mark_requirement_analysis_completed()
            project.mark_source_analysis_completed()
            await self._projects.save(project)
            await self._unit_of_work.commit()
