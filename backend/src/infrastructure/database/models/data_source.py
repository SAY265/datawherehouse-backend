"""Model CSDL đại diện cho Bảng Nguồn Dữ liệu (data_sources)."""

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_NAME_LENGTH, MAX_TYPE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import ProjectModel


class DataSourceModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng data_sources."""

    __tablename__ = "data_sources"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    type: Mapped[str] = mapped_column(String(MAX_TYPE_LENGTH), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    schema_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (Index("idx_data_sources_project_type", "project_id", "type"),)

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="data_sources")
