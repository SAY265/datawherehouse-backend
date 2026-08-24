"""Model CSDL đại diện cho Bảng Phiên Agent (project_sessions)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_STATUS_LENGTH, MAX_TITLE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import ProjectModel
    from src.infrastructure.database.models.session_event import SessionEventModel
    from src.infrastructure.database.models.user import UserModel


class ProjectSessionModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng project_sessions."""

    __tablename__ = "project_sessions"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(MAX_TITLE_LENGTH), nullable=True)
    status: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False, default="ACTIVE", index=True)

    __table_args__ = (Index("idx_project_sessions_project_status", "project_id", "status"),)

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="sessions")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="project_sessions")
    events: Mapped[list["SessionEventModel"]] = relationship(
        "SessionEventModel", back_populates="session", cascade="all, delete-orphan"
    )
