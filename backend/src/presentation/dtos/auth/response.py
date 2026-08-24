"""Safe HTTP response models for authentication."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from src.application.auth.output import AuthTokenOutput, UserOutput


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_application(cls, output: UserOutput) -> "UserResponse":
        return cls.model_validate(output)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

    @classmethod
    def from_application(cls, output: AuthTokenOutput) -> "AuthTokenResponse":
        return cls(
            access_token=output.access_token,
            token_type=output.token_type,
            user=UserResponse.from_application(output.user),
        )


class LogoutResponse(BaseModel):
    status: str = "success"
