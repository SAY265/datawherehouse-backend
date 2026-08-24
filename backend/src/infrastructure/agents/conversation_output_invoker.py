"""Khôi phục một lần khi LLM trả sai contract hội thoại thiết kế."""

from langchain_core.language_models import BaseChatModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.agent_structured_outputs import DwConversationResult
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)

OUTPUT_REPAIR_INSTRUCTION = """## Output contract correction
Your previous response did not match the required structured schema. Return all four keys:
kind, question, dbml, summary. For proposal, question must be null and dbml must contain the
complete revised raw DBML. For clarification, dbml must be null and question must be present.
Keep summary to one or two sentences and do not repeat phrases."""


class ConversationOutputInvoker:
    """Gọi structured conversation và retry đúng một lần khi output sai schema."""

    def __init__(self, chat_model: BaseChatModel, pii_guard: PiiGuard) -> None:
        self._invoker = StructuredLlmInvoker(chat_model, pii_guard)

    async def invoke(
        self, system_prompt: str, user_prompt: str
    ) -> DwConversationResult:
        """Retry với contract sửa lỗi mà không đưa raw response hỏng vào prompt."""
        try:
            return await self._invoke(system_prompt, user_prompt)
        except InfrastructureException as exc:
            if exc.code is not ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR:
                raise
            logger.warning("Retrying invalid DW conversation structured output once.")
            repaired_prompt = f"{user_prompt}\n\n{OUTPUT_REPAIR_INSTRUCTION}"
            return await self._invoke(system_prompt, repaired_prompt)

    async def _invoke(
        self, system_prompt: str, user_prompt: str
    ) -> DwConversationResult:
        return await self._invoker.invoke(
            system_prompt,
            user_prompt,
            DwConversationResult,
        )
