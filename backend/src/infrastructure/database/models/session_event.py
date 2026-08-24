"""Model CSDL đại diện cho Bảng Sự kiện Phiên (session_events)."""

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_ROLE_LENGTH, MAX_TYPE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project_session import ProjectSessionModel


class SessionEventModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng session_events."""

    __tablename__ = "session_events"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(MAX_ROLE_LENGTH), nullable=False)
    type: Mapped[str] = mapped_column(String(MAX_TYPE_LENGTH), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    __table_args__ = (Index("idx_session_events_session_created", "session_id", "created_at"),)

    # Relationships
    session: Mapped["ProjectSessionModel"] = relationship("ProjectSessionModel", back_populates="events")
