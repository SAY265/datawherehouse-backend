"""Model CSDL đại diện cho Bảng Dự án (projects)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_DOMAIN_LENGTH, MAX_NAME_LENGTH, MAX_STATUS_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.data_model import DataModelModel
    from src.infrastructure.database.models.data_source import DataSourceModel
    from src.infrastructure.database.models.project_member import ProjectMemberModel
    from src.infrastructure.database.models.project_session import ProjectSessionModel
    from src.infrastructure.database.models.requirement import RequirementModel
    from src.infrastructure.database.models.sandbox_config import SandboxConfigModel
    from src.infrastructure.database.models.user import UserModel


class ProjectModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng projects."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(MAX_DOMAIN_LENGTH), nullable=True)
    requirement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False, default="ACTIVE", index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (Index("idx_projects_user_status", "user_id", "status"),)

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="projects")
    members: Mapped[list["ProjectMemberModel"]] = relationship(
        "ProjectMemberModel", back_populates="project", cascade="all, delete-orphan", passive_deletes=True
    )
    requirements: Mapped[list["RequirementModel"]] = relationship(
        "RequirementModel", back_populates="project", cascade="all, delete-orphan", passive_deletes=True
    )
    data_sources: Mapped[list["DataSourceModel"]] = relationship(
        "DataSourceModel", back_populates="project", cascade="all, delete-orphan", passive_deletes=True
    )
    sessions: Mapped[list["ProjectSessionModel"]] = relationship(
        "ProjectSessionModel", back_populates="project", cascade="all, delete-orphan", passive_deletes=True
    )
    data_model: Mapped["DataModelModel | None"] = relationship(
        "DataModelModel", back_populates="project", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )
    sandbox_config: Mapped["SandboxConfigModel | None"] = relationship(
        "SandboxConfigModel", back_populates="project", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )
