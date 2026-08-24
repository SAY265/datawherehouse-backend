"""RequirementAgent gồm hai operation, mỗi operation gọi LLM đúng một lần."""

from uuid import UUID

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
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.infrastructure.agents.agent_context_renderer import render_analytical_input
from src.infrastructure.agents.prompts.requirement import (
    ANALYTICAL_SYSTEM_PROMPT,
    ANALYTICAL_USER_PROMPT,
    RAW_REQUIREMENT_SYSTEM_PROMPT,
    RAW_REQUIREMENT_USER_PROMPT,
)
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalRequirementItem,
    AnalyticalRequirementResult,
    RequirementStructureResult,
)
from src.infrastructure.llm.lazy_chat_model import ChatModelSource, LazyChatModel
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override


class RequirementAnalysisAgent(IRequirementAnalysisAgent):
    """Adapter provider-neutral cho RequirementAgent."""

    def __init__(self, chat_model: ChatModelSource, pii_guard: PiiGuard) -> None:
        self._model = LazyChatModel(chat_model)
        self._pii_guard = pii_guard

    @override
    async def structure_raw_requirement(
        self, data: RawRequirementAnalysisInput
    ) -> tuple[GeneratedRequirement, ...]:
        """Cấu trúc hóa Raw Requirement bằng một structured invocation."""
        result = await self._invoker().invoke(
            RAW_REQUIREMENT_SYSTEM_PROMPT,
            RAW_REQUIREMENT_USER_PROMPT.format(raw_requirement=data.raw_requirement),
            RequirementStructureResult,
        )
        return tuple(
            GeneratedRequirement(
                item.title,
                item.description,
                RequirementType(item.requirement_type),
                RequirementPriority(item.priority),
            )
            for item in result.requirements
        )

    @override
    async def derive_analytical_requirements(
        self, data: AnalyticalAnalysisInput
    ) -> tuple[GeneratedAnalyticalRequirement, ...]:
        """Sinh analytical output với source ID bắt buộc thuộc input."""
        requirements, schemas = render_analytical_input(data)
        result = await self._invoker().invoke(
            ANALYTICAL_SYSTEM_PROMPT,
            ANALYTICAL_USER_PROMPT.format(
                requirements=requirements, schema_metadata=schemas
            ),
            AnalyticalRequirementResult,
        )
        valid_ids = {str(item.id) for item in data.requirements}
        if any(item.source_requirement_id not in valid_ids for item in result.analytical_requirements):
            raise InfrastructureException(
                ErrorCode.LLM_ERROR,
                "RequirementAgent trả source_requirement_id không thuộc input.",
            )
        return tuple(_map_analytical(item) for item in result.analytical_requirements)

    def _invoker(self) -> StructuredLlmInvoker:
        """Dựng invoker nhẹ trên model đã lazy-cache."""
        return StructuredLlmInvoker(self._model.get(), self._pii_guard)


def _map_analytical(item: AnalyticalRequirementItem) -> GeneratedAnalyticalRequirement:
    """Ánh xạ Pydantic output đã kiểm tra ID sang Application output."""
    return GeneratedAnalyticalRequirement(
        UUID(item.source_requirement_id),
        item.metric,
        item.dimension,
        item.time_granularity,
        item.aggregation_method,
        item.grain,
    )
