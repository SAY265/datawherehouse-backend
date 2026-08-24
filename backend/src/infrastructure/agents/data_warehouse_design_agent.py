"""DWDesignAgent provider-neutral cho generate và revise DBML."""

from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseDesignAgent,
)
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    DataWarehouseDesignInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    ConversationDesignResult,
    GeneratedDbml,
    ValidationIssue,
)
from src.infrastructure.agents.agent_context_renderer import render_design_input
from src.infrastructure.agents.conversation_output_invoker import ConversationOutputInvoker
from src.infrastructure.agents.dbml_normalizer import normalize_agent_dbml
from src.infrastructure.agents.prompts.dw_conversation import (
    DW_CONVERSATION_SYSTEM_PROMPT,
    DW_CONVERSATION_USER_PROMPT,
)
from src.infrastructure.agents.prompts.dw_design import (
    DW_DESIGN_SYSTEM_PROMPT,
    DW_DESIGN_USER_PROMPT,
)
from src.infrastructure.agents.prompts.dw_revise import (
    DW_REVISE_SYSTEM_PROMPT,
    DW_REVISE_USER_PROMPT,
)
from src.infrastructure.llm.agent_structured_outputs import DbmlRevisionResult
from src.infrastructure.llm.lazy_chat_model import ChatModelSource, LazyChatModel
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override


class DataWarehouseDesignAgent(IDataWarehouseDesignAgent):
    """Mỗi method thực hiện đúng một structured LLM invocation."""

    def __init__(self, chat_model: ChatModelSource, pii_guard: PiiGuard) -> None:
        self._model = LazyChatModel(chat_model)
        self._pii_guard = pii_guard

    @override
    async def generate(self, data: DataWarehouseDesignInput) -> GeneratedDbml:
        """Sinh toàn bộ DBML từ ba nhóm context bắt buộc."""
        requirements, analytical, schemas = render_design_input(data)
        prompt = DW_DESIGN_USER_PROMPT.format(
            requirements=requirements,
            analytical_requirements=analytical,
            schema_metadata=schemas,
            failed_dbml=data.failed_dbml or "(none)",
            validation_issues=_render_issues(data.validation_issues),
        )
        return await self._invoke(DW_DESIGN_SYSTEM_PROMPT, prompt)

    @override
    async def revise(self, data: RevisionDesignInput) -> GeneratedDbml:
        """Sửa Current DBML bằng full project context."""
        requirements, analytical, schemas = render_design_input(data)
        prompt = DW_REVISE_USER_PROMPT.format(
            current_dbml=data.current_dbml,
            instruction=data.instruction or "Update the model to match current inputs.",
            requirements=requirements,
            analytical_requirements=analytical,
            schema_metadata=schemas,
            validation_issues=_render_issues(data.validation_issues),
        )
        return await self._invoke(DW_REVISE_SYSTEM_PROMPT, prompt)

    @override
    async def converse(self, data: ConversationDesignInput) -> ConversationDesignResult:
        """Trả câu hỏi làm rõ hoặc DBML proposal từ một structured invocation."""
        revision = data.revision
        requirements, analytical, schemas = render_design_input(revision)
        prompt = DW_CONVERSATION_USER_PROMPT.format(
            conversation=_render_conversation(data),
            current_dbml=revision.current_dbml,
            instruction=revision.instruction or "",
            requirements=requirements,
            analytical_requirements=analytical,
            schema_metadata=schemas,
        )
        result = await ConversationOutputInvoker(
            self._model.get(), self._pii_guard
        ).invoke(DW_CONVERSATION_SYSTEM_PROMPT, prompt)
        if result.kind == AgentTurnKind.CLARIFICATION:
            return ConversationDesignResult(
                AgentTurnKind.CLARIFICATION,
                question=result.question,
                summary=result.summary,
            )
        return ConversationDesignResult(
            AgentTurnKind.PROPOSAL,
            dbml=normalize_agent_dbml(result.dbml or ""),
            summary=result.summary,
        )

    async def _invoke(self, system_prompt: str, user_prompt: str) -> GeneratedDbml:
        """Gọi LLM một lần, unmask rồi chuẩn hóa DBML deterministic."""
        invoker = StructuredLlmInvoker(self._model.get(), self._pii_guard)
        result = await invoker.invoke(system_prompt, user_prompt, DbmlRevisionResult)
        return GeneratedDbml(normalize_agent_dbml(result.dbml))


def _render_issues(issues: tuple[ValidationIssue, ...]) -> str:
    """Render typed validation issues cho prompt retry."""
    lines = (
        f"[{item.severity}] {item.title}: {item.description}{_issue_location(item)}"
        for item in issues
    )
    return "\n".join(lines) or "(none)"


def _render_conversation(data: ConversationDesignInput) -> str:
    """Render lịch sử công khai, không gồm metadata nội bộ."""
    lines = (f"{item.role}: {item.content}" for item in data.history)
    return "\n".join(lines) or "(new session)"


def _issue_location(issue: ValidationIssue) -> str:
    """Render vị trí lỗi bằng tên bảng/cột dễ đọc."""
    parts = tuple(item for item in (issue.table_name, issue.column_name) if item)
    return f" ({'.'.join(parts)})" if parts else ""
