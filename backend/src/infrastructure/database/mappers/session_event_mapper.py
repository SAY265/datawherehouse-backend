"""Mapper chuyển đổi dữ liệu giữa SessionEvent Domain Entity và SessionEventModel Persistence."""

from typing import Any
from uuid import UUID

from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    AgentType,
    SessionEventRole,
    SessionEventType,
    ToolResultStatus,
)
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    LLMCallStats,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)
from src.infrastructure.database.models.session_event import SessionEventModel


class SessionEventMapper:
    """Mapper thực hiện chuyển đổi giữa SessionEvent Entity và SessionEventModel."""

    @staticmethod
    def metadata_to_dict(metadata: SessionEventMetadata | None) -> dict[str, Any] | None:
        """Chuyển đổi SessionEventMetadata Value Object sang dict JSONB."""
        if not metadata:
            return None

        if isinstance(metadata, MessageMetadata):
            return {"model": metadata.model}

        if isinstance(metadata, AgentCallMetadata):
            return {
                "caller_agent": str(
                    metadata.caller_agent.value if hasattr(metadata.caller_agent, "value") else metadata.caller_agent
                ),
                "target_agent": str(
                    metadata.target_agent.value if hasattr(metadata.target_agent, "value") else metadata.target_agent
                ),
                "input": metadata.input_data,
            }

        if isinstance(metadata, AgentResultMetadata):
            llm_dict = None
            if metadata.llm:
                llm_dict = {
                    "provider": metadata.llm.provider,
                    "model": metadata.llm.model,
                    "input_tokens": metadata.llm.input_tokens,
                    "output_tokens": metadata.llm.output_tokens,
                    "total_tokens": metadata.llm.total_tokens,
                    "temperature": metadata.llm.temperature,
                    "latency_ms": metadata.llm.latency_ms,
                    "finish_reason": metadata.llm.finish_reason,
                }

            return {
                "session_event_id": str(metadata.session_event_id),
                "agent": str(metadata.agent.value if hasattr(metadata.agent, "value") else metadata.agent),
                "status": str(metadata.status.value if hasattr(metadata.status, "value") else metadata.status),
                "output": metadata.output_data,
                "error": metadata.error,
                "llm": llm_dict,
            }

        if isinstance(metadata, ToolCallMetadata):
            return {
                "agent": str(metadata.agent.value if hasattr(metadata.agent, "value") else metadata.agent),
                "tool": metadata.tool,
                "arguments": metadata.arguments,
            }

        if isinstance(metadata, ToolResultMetadata):
            return {
                "session_event_id": str(metadata.session_event_id),
                "tool": metadata.tool,
                "status": str(metadata.status.value if hasattr(metadata.status, "value") else metadata.status),
                "result": metadata.result_data,
                "error": metadata.error,
            }

        return None

    @staticmethod
    def dict_to_metadata(data: dict[str, Any] | None, event_type: SessionEventType) -> SessionEventMetadata | None:
        """Chuyển đổi dict JSONB từ CSDL sang SessionEventMetadata Value Object phù hợp."""
        if not data:
            return None

        if event_type == SessionEventType.MESSAGE:
            return MessageMetadata(model=data.get("model"))

        if event_type == SessionEventType.AGENT_CALL:
            return AgentCallMetadata(
                caller_agent=AgentType(data["caller_agent"]),
                target_agent=AgentType(data["target_agent"]),
                input_data=data.get("input", ""),
            )

        if event_type == SessionEventType.AGENT_RESULT:
            llm_obj = None
            if "llm" in data and isinstance(data["llm"], dict):
                l_dict = data["llm"]
                llm_obj = LLMCallStats(
                    provider=l_dict.get("provider", ""),
                    model=l_dict.get("model", ""),
                    input_tokens=l_dict.get("input_tokens", 0),
                    output_tokens=l_dict.get("output_tokens", 0),
                    total_tokens=l_dict.get("total_tokens", 0),
                    temperature=l_dict.get("temperature", 1.0),
                    latency_ms=l_dict.get("latency_ms", 0),
                    finish_reason=l_dict.get("finish_reason"),
                )

            raw_ev_id = data.get("session_event_id")
            ev_id = UUID(raw_ev_id) if isinstance(raw_ev_id, str) else raw_ev_id
            return AgentResultMetadata(
                agent=AgentType(data["agent"]),
                status=AgentResultStatus(data["status"]),
                session_event_id=ev_id,
                output_data=data.get("output"),
                error=data.get("error"),
                llm=llm_obj,
            )

        if event_type == SessionEventType.TOOL_CALL:
            return ToolCallMetadata(
                agent=AgentType(data["agent"]),
                tool=data.get("tool", ""),
                arguments=data.get("arguments"),
            )

        if event_type == SessionEventType.TOOL_RESULT:
            raw_ev_id = data.get("session_event_id")
            ev_id = UUID(raw_ev_id) if isinstance(raw_ev_id, str) else raw_ev_id
            return ToolResultMetadata(
                tool=data.get("tool", ""),
                status=ToolResultStatus(data["status"]),
                session_event_id=ev_id,
                result_data=data.get("result"),
                error=data.get("error"),
            )

        return None

    @classmethod
    def to_domain(cls, model: SessionEventModel) -> SessionEvent:
        """Chuyển đổi từ SessionEventModel (Persistence) sang SessionEvent (Domain Entity)."""
        ev_type = SessionEventType(model.type)
        return SessionEvent(
            id=model.id,
            session_id=model.session_id,
            role=SessionEventRole(model.role),
            type=ev_type,
            content=model.content,
            metadata=cls.dict_to_metadata(model.event_metadata, ev_type),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_model(cls, entity: SessionEvent) -> SessionEventModel:
        """Chuyển đổi từ SessionEvent (Domain Entity) sang SessionEventModel (Persistence)."""
        return SessionEventModel(
            id=entity.id,
            session_id=entity.session_id,
            role=str(entity.role.value if hasattr(entity.role, "value") else entity.role),
            type=str(entity.type.value if hasattr(entity.type, "value") else entity.type),
            content=entity.content,
            event_metadata=cls.metadata_to_dict(entity.metadata),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    def update_model(cls, model: SessionEventModel, entity: SessionEvent) -> SessionEventModel:
        """Cập nhật dữ liệu từ SessionEvent Entity sang SessionEventModel đã tồn tại."""
        model.session_id = entity.session_id
        model.role = str(entity.role.value if hasattr(entity.role, "value") else entity.role)
        model.type = str(entity.type.value if hasattr(entity.type, "value") else entity.type)
        model.content = entity.content
        model.event_metadata = cls.metadata_to_dict(entity.metadata)
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        return model
