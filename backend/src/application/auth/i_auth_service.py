"""Application contract for authentication."""

from abc import ABC, abstractmethod

from src.application.auth.input import LoginInput, RegisterInput
from src.application.auth.output import AuthTokenOutput, UserOutput
from src.domain.shared.types import EntityID


class IAuthService(ABC):
    """Application contract for authentication use cases."""

    @abstractmethod
    async def register(self, data: RegisterInput) -> AuthTokenOutput:
        raise NotImplementedError

    @abstractmethod
    async def login(self, data: LoginInput) -> AuthTokenOutput:
        raise NotImplementedError

    @abstractmethod
    async def get_current_user(self, user_id: EntityID) -> UserOutput:
        raise NotImplementedError

    @abstractmethod
    async def logout(self, access_token: str) -> None:
        raise NotImplementedError
