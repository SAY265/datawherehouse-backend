"""Public service contract và outbound ports của workflow kho dữ liệu."""

from abc import ABC, abstractmethod

from src.application.data_models.output import ChangeProposalDetailOutput, DataModelOutput
from src.application.data_warehouse_workflows.input import (
    AnalyticalAnalysisInput,
    ConversationDesignInput,
    CreateAgentTurnInput,
    CreateAiEditProposalInput,
    DataWarehouseDesignInput,
    GenerateDataModelInput,
    GetAnalysisStatusInput,
    RawRequirementAnalysisInput,
    ReanalyzeProjectInput,
    RegenerateDataModelInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    AgentTurnOutput,
    AnalysisStatusOutput,
    ConversationDesignResult,
    GeneratedAnalyticalRequirement,
    GeneratedDbml,
    GeneratedRequirement,
    ValidationIssue,
)


class IRequirementAnalysisAgent(ABC):
    """Outbound port cho hai operation của RequirementAgent."""

    @abstractmethod
    async def structure_raw_requirement(self, data: RawRequirementAnalysisInput) -> tuple[GeneratedRequirement, ...]:
        """Cấu trúc hóa Raw Requirement bằng đúng một LLM invocation."""

    @abstractmethod
    async def derive_analytical_requirements(
        self, data: AnalyticalAnalysisInput
    ) -> tuple[GeneratedAnalyticalRequirement, ...]:
        """Sinh AnalyticalRequirements bằng đúng một LLM invocation."""


class IDataWarehouseDesignAgent(ABC):
    """Outbound port cho các operation của DWDesignAgent."""

    @abstractmethod
    async def generate(self, data: DataWarehouseDesignInput) -> GeneratedDbml:
        """Sinh DBML ban đầu bằng đúng một LLM invocation."""

    @abstractmethod
    async def revise(self, data: RevisionDesignInput) -> GeneratedDbml:
        """Sinh DBML đề xuất bằng đúng một LLM invocation."""
    @abstractmethod
    async def converse(self, data: ConversationDesignInput) -> ConversationDesignResult:
        """Trả câu hỏi làm rõ hoặc DBML proposal trong một invocation."""


class IDataModelValidationEngine(ABC):
    """Outbound port cho ValidationEngine deterministic."""

    @abstractmethod
    def validate(self, dbml: str) -> tuple[ValidationIssue, ...]:
        """Trả toàn bộ lỗi và cảnh báo của DBML."""


class IDataWarehouseWorkflowService(ABC):
    """Hợp đồng điều phối workflow từ action rõ ràng của người dùng."""

    @abstractmethod
    async def get_analysis_status(self, data: GetAnalysisStatusInput) -> AnalysisStatusOutput:
        """Đọc trạng thái đồng bộ mà không gọi Agent."""

    @abstractmethod
    async def generate_data_model(self, data: GenerateDataModelInput) -> DataModelOutput:
        """Phân tích input và tạo Data Model đầu tiên."""

    @abstractmethod
    async def reanalyze(self, data: ReanalyzeProjectInput) -> AnalysisStatusOutput:
        """Phân tích input đã đổi nhưng không sửa Data Model."""

    @abstractmethod
    async def regenerate_data_model(self, data: RegenerateDataModelInput) -> DataModelOutput:
        """Tạo lại và ghi đè Data Model hiện hành sau validation."""

    @abstractmethod
    async def create_agent_turn(self, data: CreateAgentTurnInput) -> AgentTurnOutput:
        """Tạo lượt hội thoại có thể trả clarification hoặc proposal."""

    @abstractmethod
    async def create_ai_edit_proposal(self, data: CreateAiEditProposalInput) -> ChangeProposalDetailOutput:
        """Tạo proposal AI edit để Human Review."""
