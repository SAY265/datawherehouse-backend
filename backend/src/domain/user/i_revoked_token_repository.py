"""Repository contract cho JWT revocation bền vững."""

from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.user.revoked_token import RevokedToken


class IRevokedTokenRepository(ABC):
    @abstractmethod
    async def exists(self, jti: str) -> bool: ...

    @abstractmethod
    async def save(self, token: RevokedToken) -> None: ...

    @abstractmethod
    async def delete_expired(self, now: datetime) -> None: ...
