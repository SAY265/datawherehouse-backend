"""Mapper giữa SessionEvent Domain entity và ORM model."""

from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import SessionEventRole, SessionEventType
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)
from src.infrastructure.database.mappers.session_event.session_event_metadata_codec import (
    decode_event_metadata,
    encode_event_metadata,
)
from src.infrastructure.database.models.session_event import SessionEventModel

_METADATA_TYPES: dict[SessionEventType, type[SessionEventMetadata]] = {
    SessionEventType.MESSAGE: MessageMetadata,
    SessionEventType.AGENT_CALL: AgentCallMetadata,
    SessionEventType.AGENT_RESULT: AgentResultMetadata,
    SessionEventType.TOOL_CALL: ToolCallMetadata,
    SessionEventType.TOOL_RESULT: ToolResultMetadata,
}


class SessionEventMapper:
    """Ánh xạ SessionEvent và giao codec xử lý JSONB metadata."""

    @staticmethod
    def to_domain(model: SessionEventModel) -> SessionEvent:
        """Khôi phục SessionEvent từ ORM model."""
        event_type = SessionEventType(model.type)
        return SessionEvent(
            id=model.id,
            session_id=model.session_id,
            role=SessionEventRole(model.role),
            type=event_type,
            content=model.content,
            metadata=decode_event_metadata(model.event_metadata, _METADATA_TYPES.get(event_type)),
            turn_id=model.turn_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: SessionEvent) -> SessionEventModel:
        """Tạo ORM model từ SessionEvent."""
        return SessionEventModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role.value,
            type=entity.type.value,
            content=entity.content,
            event_metadata=encode_event_metadata(entity.metadata),
            turn_id=entity.turn_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: SessionEventModel, entity: SessionEvent) -> SessionEventModel:
        """Cập nhật các trường có thể thay đổi của ORM model."""
        model.session_id = entity.session_id
        model.role = entity.role.value
        model.type = entity.type.value
        model.content = entity.content
        model.event_metadata = encode_event_metadata(entity.metadata)
        model.turn_id = entity.turn_id
        model.updated_at = entity.updated_at
        return model
