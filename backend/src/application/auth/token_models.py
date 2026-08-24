"""Typed models trao đổi với JWT outbound port."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class IssuedToken:
    value: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class TokenClaims:
    user_id: EntityID
    jti: str
    issued_at: datetime
    expires_at: datetime
