"""Application input for user registration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterInput:
    username: str
    email: str
    password: str
    full_name: str | None = None
