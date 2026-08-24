"""Model CSDL đại diện cho Bảng Yêu cầu Phân tích (analytical_requirements)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import (
    MAX_AGGREGATION_LENGTH,
    MAX_DIMENSION_LENGTH,
    MAX_GRANULARITY_LENGTH,
    MAX_METRIC_LENGTH,
)

if TYPE_CHECKING:
    from src.infrastructure.database.models.requirement import RequirementModel


class AnalyticalRequirementModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng analytical_requirements."""

    __tablename__ = "analytical_requirements"

    requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric: Mapped[str | None] = mapped_column(String(MAX_METRIC_LENGTH), nullable=True)
    dimension: Mapped[str | None] = mapped_column(String(MAX_DIMENSION_LENGTH), nullable=True)
    time_granularity: Mapped[str | None] = mapped_column(String(MAX_GRANULARITY_LENGTH), nullable=True)
    aggregation_method: Mapped[str | None] = mapped_column(String(MAX_AGGREGATION_LENGTH), nullable=True)
    grain: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    requirement: Mapped["RequirementModel"] = relationship("RequirementModel", back_populates="analytical_requirements")
