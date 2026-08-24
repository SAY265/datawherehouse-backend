"""Model CSDL đại diện cho Bảng Thành viên Dự án (project_members)."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.utils.datetime import utc_now
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_ROLE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import ProjectModel
    from src.infrastructure.database.models.user import UserModel


class ProjectMemberModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng project_members."""

    __tablename__ = "project_members"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(MAX_ROLE_LENGTH), nullable=False, default="MEMBER")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
        Index("idx_project_members_project_user", "project_id", "user_id"),
    )

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="members")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="project_memberships")
