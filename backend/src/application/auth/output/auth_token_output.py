"""Safe authentication output models."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.types import EntityID
from src.domain.user.entities import User


@dataclass(frozen=True)
class UserOutput:
    id: EntityID
    username: str
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserOutput":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email.value,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )


@dataclass(frozen=True)
class AuthTokenOutput:
    access_token: str
    token_type: str
    user: UserOutput
