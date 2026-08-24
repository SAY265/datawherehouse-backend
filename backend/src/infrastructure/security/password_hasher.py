"""bcrypt adapter cho password hashing."""

import bcrypt
from src.application.auth.i_auth_service import IPasswordHasher
from typing_extensions import override

BCRYPT_ROUNDS = 12


class BcryptPasswordHasher(IPasswordHasher):
    """Hash passwords with bcrypt cost 12 and verify without leaking parser errors."""

    @override
    def hash(self, password: str) -> str:
        encoded = password.encode("utf-8")
        return bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("ascii")

    @override
    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
        except (ValueError, UnicodeError):
            return False
