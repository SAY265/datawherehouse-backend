"""SQLAlchemy model cho JWT revocation."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database.base import Base


class RevokedTokenModel(Base):
    """Durable revoked access-token identifier with user ownership and expiry."""

    __tablename__ = "revoked_auth_tokens"

    jti: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_revoked_auth_tokens_expires_at", "expires_at"),)
