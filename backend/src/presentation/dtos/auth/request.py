"""Validated HTTP request models for authentication."""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.application.auth.input import LoginInput, RegisterInput

USERNAME_PATTERN = r"^[A-Za-z0-9_.-]+$"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=100, pattern=USERNAME_PATTERN)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=72)
    full_name: str | None = Field(default=None, max_length=150)

    @field_validator("username", "email", "full_name", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    def to_application(self) -> RegisterInput:
        return RegisterInput(
            username=self.username,
            email=self.email,
            password=self.password,
            full_name=self.full_name,
        )


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("identifier", mode="before")
    @classmethod
    def strip_identifier(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    def to_application(self) -> LoginInput:
        return LoginInput(identifier=self.identifier, password=self.password)
