"""Model CSDL đại diện cho Bảng Đề xuất Thay đổi Mô hình Dữ liệu (data_model_changes)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_STATUS_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.data_model import DataModelModel
    from src.infrastructure.database.models.user import UserModel


class DataModelChangeModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng data_model_changes."""

    __tablename__ = "data_model_changes"

    data_model_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    base_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    proposed_dbml: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False, default="PROPOSED")
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    data_model: Mapped["DataModelModel"] = relationship("DataModelModel", back_populates="changes")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="data_model_changes")
