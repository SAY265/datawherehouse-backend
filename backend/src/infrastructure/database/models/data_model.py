"""Model CSDL đại diện cho Bảng Mô hình Dữ liệu (data_models)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.data_model_change import DataModelChangeModel
    from src.infrastructure.database.models.project import ProjectModel


class DataModelModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng data_models."""

    __tablename__ = "data_models"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    dbml: Mapped[str] = mapped_column(Text, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="data_model")
    changes: Mapped[list["DataModelChangeModel"]] = relationship(
        "DataModelChangeModel", back_populates="data_model", cascade="all, delete-orphan"
    )
