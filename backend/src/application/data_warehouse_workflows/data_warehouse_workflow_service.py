"""Application service điều phối các action trong data_flow.md."""

from copy import copy

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.output import (
    ChangeProposalDetailOutput,
    DataModelOutput,
)
from src.application.data_warehouse_workflows.analysis_runner import WorkflowAnalysisRunner
from src.application.data_warehouse_workflows.design_runner import WorkflowDesignRunner
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataModelValidationEngine,
    IDataWarehouseDesignAgent,
    IDataWarehouseWorkflowService,
    IRequirementAnalysisAgent,
)
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    CreateAgentTurnInput,
    CreateAiEditProposalInput,
    DataWarehouseDesignInput,
    GenerateDataModelInput,
    GetAnalysisStatusInput,
    ReanalyzeProjectInput,
    RegenerateDataModelInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    AgentTurnOutput,
    AnalysisStatusOutput,
)
from src.application.data_warehouse_workflows.source_analysis_runner import (
    WorkflowSourceAnalysisRunner,
)
from src.application.data_warehouse_workflows.workflow_data_loader import WorkflowDataReader
from src.application.data_warehouse_workflows.workflow_persistence import (
    WorkflowPersistence,
    raise_model_exists,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.data_model.entities import DataModel
from src.domain.data_model.i_data_model_change_repository import IDataModelChangeRepository
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.entities import Project
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from src.domain.shared.types import EntityID
from typing_extensions import override


class DataWarehouseWorkflowService(IDataWarehouseWorkflowService):
    """Điều phối Agent, validation và persistence theo action rõ ràng."""

    def __init__(
        self,
        projects: IProjectRepository,
        requirements: IRequirementRepository,
        analytical: IAnalyticalRequirementRepository,
        data_sources: IDataSourceRepository,
        models: IDataModelRepository,
        changes: IDataModelChangeRepository,
        requirement_agent: IRequirementAnalysisAgent,
        source_analysis: WorkflowSourceAnalysisRunner,
        design_agent: IDataWarehouseDesignAgent,
        validator: IDataModelValidationEngine,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
    ) -> None:
        self._models = models
        self._unit_of_work = unit_of_work
        self._access = access
        self._reader = WorkflowDataReader(requirements, analytical, data_sources, models)
        self._analysis = WorkflowAnalysisRunner(
            projects,
            requirements,
            analytical,
            requirement_agent,
            unit_of_work,
            access,
            self._reader,
            source_analysis,
        )
        self._design = WorkflowDesignRunner(design_agent, validator)
        self._persistence = WorkflowPersistence(models, changes, unit_of_work, access)

    @override
    async def get_analysis_status(self, data: GetAnalysisStatusInput) -> AnalysisStatusOutput:
        """Tính trạng thái outdated mà không gọi LLM."""
        project = (await self._access.require_member(data.project_id)).project
        return await self._reader.calculate_analysis_status(project)

    @override
    async def reanalyze(self, data: ReanalyzeProjectInput) -> AnalysisStatusOutput:
        """Chạy các RequirementAgent operation cần thiết."""
        project = await self._analysis.run(data.project_id)
        return await self._reader.calculate_analysis_status(project)

    @override
    async def generate_data_model(self, data: GenerateDataModelInput) -> DataModelOutput:
        """Phân tích input và chỉ tạo snapshot khi Project chưa có model."""
        await self._ensure_model_absent(data.project_id)
        project = await self._analysis.run(data.project_id)
        project_snapshot = copy(project)
        design_input = await self._reader.load_design_input(project.id)
        await self._unit_of_work.rollback()
        generated = await self._design.generate(design_input)
        saved = await self._persistence.persist_initial(project_snapshot, generated.dbml)
        return DataModelOutput.from_domain(saved, is_outdated=False)

    @override
    async def regenerate_data_model(self, data: RegenerateDataModelInput) -> DataModelOutput:
        """Sinh lại từ analysis hiện hành và ghi đè snapshot trực tiếp."""
        project = await self._access.require_owner(data.project_id)
        await self._ensure_analysis_current(project)
        project_snapshot = copy(project)
        design_input = await self._reader.load_design_input(project.id)
        model = await self._require_model(data.project_id)
        await self._unit_of_work.rollback()
        generated = await self._design.generate(design_input)
        saved = await self._persistence.persist_regenerated(
            model,
            project_snapshot,
            generated.dbml,
        )
        return DataModelOutput.from_domain(saved, is_outdated=False)

    @override
    async def create_ai_edit_proposal(self, data: CreateAiEditProposalInput) -> ChangeProposalDetailOutput:
        """Sinh proposal từ context hiện hành và không sửa snapshot."""
        project = await self._access.require_owner(data.project_id)
        await self._ensure_analysis_current(project)
        project_snapshot = copy(project)
        design_input = await self._reader.load_design_input(project.id)
        model = await self._require_model(data.project_id)
        await self._unit_of_work.rollback()
        revision_input = self._revision_input(design_input, model, data.instruction)
        generated = await self._design.revise(revision_input)
        change = await self._persistence.persist_proposal(model, project_snapshot, generated.dbml)
        return ChangeProposalDetailOutput.from_domain(change, model)

    @override
    async def create_agent_turn(self, data: CreateAgentTurnInput) -> AgentTurnOutput:
        """Trả clarification hoặc persist proposal từ hội thoại session."""
        project = await self._access.require_owner(data.project_id)
        await self._ensure_analysis_current(project)
        project_snapshot = copy(project)
        design_input = await self._reader.load_design_input(project.id)
        model = await self._require_model(data.project_id)
        await self._unit_of_work.rollback()
        revision = self._revision_input(design_input, model, data.instruction)
        result = await self._design.converse(ConversationDesignInput(revision, data.history))
        if result.kind is AgentTurnKind.CLARIFICATION:
            return AgentTurnOutput(
                result.kind, question=result.question, summary=result.summary
            )
        change = await self._persistence.persist_proposal(
            model,
            project_snapshot,
            result.dbml or "",
        )
        proposal = ChangeProposalDetailOutput.from_domain(change, model)
        return AgentTurnOutput(
            AgentTurnKind.PROPOSAL, proposal=proposal, summary=result.summary
        )

    async def _ensure_analysis_current(self, project: Project) -> None:
        """Chặn design khi Requirement hoặc Source analysis đã outdated."""
        status = await self._reader.calculate_analysis_status(project)
        if status.requirement_analysis_outdated or status.source_analysis_outdated:
            raise BusinessException(
                ErrorCode.DATA_MODEL_ANALYSIS_OUTDATED,
                "Cần Analyze Changes trước khi cập nhật Data Model.",
            )

    @staticmethod
    def _revision_input(
        design_input: DataWarehouseDesignInput,
        model: DataModel,
        instruction: str,
    ) -> RevisionDesignInput:
        return RevisionDesignInput(
            design_input.requirements,
            design_input.analytical_requirements,
            design_input.data_sources,
            model.dbml,
            instruction,
        )

    async def _ensure_model_absent(self, project_id: EntityID) -> None:
        """Bảo vệ endpoint initial generation khỏi overwrite."""
        await self._access.require_owner(project_id)
        if await self._models.get_by_project_id(project_id):
            raise_model_exists()

    async def _require_model(self, project_id: EntityID) -> DataModel:
        """Lấy Data Model hoặc báo not found."""
        model = await self._models.get_by_project_id(project_id)
        if model is None:
            raise BusinessException(ErrorCode.DATA_MODEL_NOT_FOUND, "Không tìm thấy Data Model.")
        return model
