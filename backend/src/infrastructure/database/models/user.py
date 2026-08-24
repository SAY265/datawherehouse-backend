"""Model CSDL đại diện cho Bảng Người dùng (users)."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.data_model_change import DataModelChangeModel
    from src.infrastructure.database.models.project import ProjectModel
    from src.infrastructure.database.models.project_member import ProjectMemberModel
    from src.infrastructure.database.models.project_session import ProjectSessionModel


class UserModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng users."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(MAX_USERNAME_LENGTH), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(MAX_EMAIL_LENGTH), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="USER")

    # Relationships
    projects: Mapped[list["ProjectModel"]] = relationship(
        "ProjectModel", back_populates="user", cascade="all, delete-orphan"
    )
    project_memberships: Mapped[list["ProjectMemberModel"]] = relationship(
        "ProjectMemberModel", back_populates="user", cascade="all, delete-orphan"
    )
    project_sessions: Mapped[list["ProjectSessionModel"]] = relationship(
        "ProjectSessionModel", back_populates="user", cascade="all, delete-orphan"
    )
    data_model_changes: Mapped[list["DataModelChangeModel"]] = relationship(
        "DataModelChangeModel", back_populates="user"
    )
