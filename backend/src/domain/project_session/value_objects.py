"""Value Objects thuộc miền Phiên Agent (Project Session)."""

from dataclasses import dataclass

from src.domain.project_session.enums import AgentResultStatus, AgentType, ToolResultStatus
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject

DEFAULT_CANCELLED_ERROR_MESSAGE = "Agent execution was cancelled"


@dataclass(frozen=True)
class LLMCallStats(BaseValueObject):
    """Thông tin chi tiết về cuộc gọi LLM (Token, Latency, Model)."""

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    temperature: float = 1.0
    latency_ms: int = 0
    finish_reason: str | None = None


@dataclass(frozen=True)
class MessageMetadata(BaseValueObject):
    """Metadata cho sự kiện dạng Tin nhắn (MESSAGE)."""

    model: str | None = None


@dataclass(frozen=True)
class AgentCallMetadata(BaseValueObject):
    """Metadata khi một Agent gọi Agent khác (AGENT_CALL)."""

    caller_agent: AgentType
    target_agent: AgentType
    input_data: str

    def __post_init__(self) -> None:
        """Đảm bảo các thuộc tính agent được convert sang AgentType enum nếu truyền chuỗi str."""
        if isinstance(self.caller_agent, str):
            object.__setattr__(self, "caller_agent", AgentType(self.caller_agent))
        if isinstance(self.target_agent, str):
            object.__setattr__(self, "target_agent", AgentType(self.target_agent))


@dataclass(frozen=True)
class AgentResultMetadata(BaseValueObject):
    """Metadata kết quả thực thi của Agent (AGENT_RESULT)."""

    agent: AgentType
    status: AgentResultStatus
    session_event_id: EntityID
    output_data: str | None = None
    error: str | None = None
    llm: LLMCallStats | None = None

    def __post_init__(self) -> None:
        """Đảm bảo thuộc tính agent & status được convert sang Enum và gán message mặc định cho CANCELLED."""
        if isinstance(self.agent, str):
            object.__setattr__(self, "agent", AgentType(self.agent))
        if isinstance(self.status, str):
            object.__setattr__(self, "status", AgentResultStatus(self.status))

        if self.status == AgentResultStatus.CANCELLED and not self.error:
            object.__setattr__(self, "error", DEFAULT_CANCELLED_ERROR_MESSAGE)


@dataclass(frozen=True)
class ToolCallMetadata(BaseValueObject):
    """Metadata khi Agent gọi Tool (TOOL_CALL)."""

    agent: AgentType
    tool: str
    arguments: str | None = None

    def __post_init__(self) -> None:
        """Đảm bảo agent được convert sang AgentType enum nếu truyền chuỗi str."""
        if isinstance(self.agent, str):
            object.__setattr__(self, "agent", AgentType(self.agent))


@dataclass(frozen=True)
class ToolResultMetadata(BaseValueObject):
    """Metadata kết quả trả về từ Tool (TOOL_RESULT)."""

    tool: str
    status: ToolResultStatus
    session_event_id: EntityID
    result_data: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        """Đảm bảo status được convert sang ToolResultStatus enum nếu truyền chuỗi str."""
        if isinstance(self.status, str):
            object.__setattr__(self, "status", ToolResultStatus(self.status))


SessionEventMetadata = MessageMetadata | AgentCallMetadata | AgentResultMetadata | ToolCallMetadata | ToolResultMetadata
