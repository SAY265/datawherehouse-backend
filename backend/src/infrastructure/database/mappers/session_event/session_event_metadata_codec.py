"""Codec JSONB cho metadata của SessionEvent."""

from uuid import UUID

from pydantic import ValidationError
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    LLMCallStats,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)
from src.domain.shared.types import JsonValue
from src.infrastructure.database.mappers.session_event.session_event_metadata_records import (
    AgentCallRecord,
    AgentResultRecord,
    LlmRecord,
    MessageRecord,
    MetadataRecord,
    ToolCallRecord,
    ToolResultRecord,
)


def encode_event_metadata(metadata: SessionEventMetadata | None) -> dict[str, JsonValue] | None:
    """Chuyển metadata Domain thành payload JSONB."""
    if metadata is None:
        return None
    record = _to_record(metadata)
    return record.model_dump(mode="json")


def decode_event_metadata(
    payload: dict[str, JsonValue] | None,
    metadata_type: type[SessionEventMetadata] | None,
) -> SessionEventMetadata | None:
    """Khôi phục metadata theo contract của event type."""
    if payload is None or metadata_type is None:
        return None
    try:
        return _from_payload(payload, metadata_type)
    except (ValidationError, ValueError) as exc:
        raise InfrastructureException(
            code=ErrorCode.DATABASE_ERROR,
            message="Metadata sự kiện phiên trong cơ sở dữ liệu không hợp lệ.",
        ) from exc


def _to_record(metadata: SessionEventMetadata) -> MetadataRecord:
    if isinstance(metadata, MessageMetadata):
        return MessageRecord(model=metadata.model)
    if isinstance(metadata, AgentCallMetadata):
        return AgentCallRecord(
            caller_agent=metadata.caller_agent,
            target_agent=metadata.target_agent,
            input=metadata.input_data,
        )
    if isinstance(metadata, AgentResultMetadata):
        return _agent_result_record(metadata)
    if isinstance(metadata, ToolCallMetadata):
        return ToolCallRecord(agent=metadata.agent, tool=metadata.tool, arguments=metadata.arguments)
    return _tool_result_record(metadata)


def _agent_result_record(metadata: AgentResultMetadata) -> AgentResultRecord:
    """Mã hóa metadata kết quả agent."""
    llm = LlmRecord.model_validate(vars(metadata.llm)) if metadata.llm else None
    return AgentResultRecord(
        session_event_id=str(metadata.session_event_id),
        agent=metadata.agent,
        status=metadata.status,
        output=metadata.output_data,
        error=metadata.error,
        llm=llm,
    )


def _tool_result_record(metadata: ToolResultMetadata) -> ToolResultRecord:
    """Mã hóa metadata kết quả tool."""
    return ToolResultRecord(
        session_event_id=str(metadata.session_event_id),
        tool=metadata.tool,
        status=metadata.status,
        result=metadata.result_data,
        error=metadata.error,
    )


def _from_payload(
    payload: dict[str, JsonValue],
    metadata_type: type[SessionEventMetadata],
) -> SessionEventMetadata:
    if metadata_type is MessageMetadata:
        return MessageMetadata(**MessageRecord.model_validate(payload).model_dump())
    if metadata_type is AgentCallMetadata:
        record = AgentCallRecord.model_validate(payload)
        return AgentCallMetadata(record.caller_agent, record.target_agent, record.input)
    if metadata_type is AgentResultMetadata:
        return _agent_result_from_payload(payload)
    if metadata_type is ToolCallMetadata:
        record = ToolCallRecord.model_validate(payload)
        return ToolCallMetadata(record.agent, record.tool, record.arguments)
    record = ToolResultRecord.model_validate(payload)
    return ToolResultMetadata(
        record.tool, record.status, UUID(record.session_event_id), record.result, record.error
    )


def _agent_result_from_payload(payload: dict[str, JsonValue]) -> AgentResultMetadata:
    record = AgentResultRecord.model_validate(payload)
    llm = LLMCallStats(**record.llm.model_dump()) if record.llm else None
    return AgentResultMetadata(
        record.agent,
        record.status,
        UUID(record.session_event_id),
        record.output,
        record.error,
        llm,
    )
