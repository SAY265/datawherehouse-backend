"""Model CSDL đại diện cho Bảng Yêu cầu (requirements)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_ROLE_LENGTH, MAX_TITLE_LENGTH, MAX_TYPE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.analytical_requirement import AnalyticalRequirementModel
    from src.infrastructure.database.models.project import ProjectModel


class RequirementModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng requirements."""

    __tablename__ = "requirements"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(MAX_TYPE_LENGTH), nullable=False)
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(MAX_ROLE_LENGTH), nullable=False, default="MEDIUM")

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="requirements")
    analytical_requirements: Mapped[list["AnalyticalRequirementModel"]] = relationship(
        "AnalyticalRequirementModel", back_populates="requirement", cascade="all, delete-orphan"
    )
