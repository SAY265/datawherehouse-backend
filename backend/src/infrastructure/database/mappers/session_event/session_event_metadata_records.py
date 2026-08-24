"""Pydantic record cho payload JSONB của SessionEvent."""

from pydantic import BaseModel, ConfigDict
from src.domain.project_session.enums import AgentResultStatus, AgentType, ToolResultStatus


class MetadataRecord(BaseModel):
    """Base record cấm trường JSON không thuộc contract."""

    model_config = ConfigDict(extra="forbid")


class MessageRecord(MetadataRecord):
    """Record metadata của message."""

    model: str | None = None


class AgentCallRecord(MetadataRecord):
    """Record metadata của agent call."""

    caller_agent: AgentType
    target_agent: AgentType
    input: str


class LlmRecord(MetadataRecord):
    """Record thống kê một lần gọi LLM."""

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    temperature: float
    latency_ms: int
    finish_reason: str | None = None


class AgentResultRecord(MetadataRecord):
    """Record metadata của agent result."""

    session_event_id: str
    agent: AgentType
    status: AgentResultStatus
    output: str | None = None
    error: str | None = None
    llm: LlmRecord | None = None


class ToolCallRecord(MetadataRecord):
    """Record metadata của tool call."""

    agent: AgentType
    tool: str
    arguments: str | None = None


class ToolResultRecord(MetadataRecord):
    """Record metadata của tool result."""

    session_event_id: str
    tool: str
    status: ToolResultStatus
    result: str | None = None
    error: str | None = None
