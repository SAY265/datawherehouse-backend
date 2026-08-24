"""Application input for user login."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginInput:
    identifier: str
    password: str
