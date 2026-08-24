"""Model CSDL đại diện cho Bảng Cấu hình Sandbox (sandbox_configs)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_NAME_LENGTH, MAX_STATUS_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import ProjectModel


class SandboxConfigModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng sandbox_configs."""

    __tablename__ = "sandbox_configs"
    __table_args__ = (
        CheckConstraint("db_type = 'POSTGRESQL'", name="ck_sandbox_configs_db_type"),
        CheckConstraint("port BETWEEN 1 AND 65535", name="ck_sandbox_configs_port"),
        CheckConstraint(
            "schema_name IS NULL OR schema_name ~ '^[A-Za-z_][A-Za-z0-9_]*$'",
            name="ck_sandbox_configs_schema_name",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    db_type: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False, default="POSTGRESQL")
    host: Mapped[str] = mapped_column(String(255), nullable=False, default="localhost")
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=5432)
    database_name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False, default="sandbox_db")
    username: Mapped[str | None] = mapped_column(String(MAX_NAME_LENGTH), nullable=True)
    password: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema_name: Mapped[str | None] = mapped_column(String(MAX_NAME_LENGTH), nullable=True, default="public")
    status: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False, default="CONFIGURED")

    # Relationship
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="sandbox_config", passive_deletes=True)
