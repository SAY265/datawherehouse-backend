"""Password hashing helpers backed by bcrypt."""

import bcrypt

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_BYTES = 72
_BCRYPT_ROUNDS = 12


def validate_password_strength(plain_password: str) -> None:
    """Reject passwords that are too short or exceed bcrypt's safe input size."""
    if len(plain_password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Mật khẩu phải có ít nhất {MIN_PASSWORD_LENGTH} ký tự.")
    if len(plain_password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Mật khẩu không được vượt quá {MAX_PASSWORD_BYTES} byte.")
    if not any(character.isalpha() for character in plain_password):
        raise ValueError("Mật khẩu phải có ít nhất một chữ cái.")
    if not any(character.isdigit() for character in plain_password):
        raise ValueError("Mật khẩu phải có ít nhất một chữ số.")


def hash_password(plain_password: str) -> str:
    """Hash a validated password with a fresh bcrypt salt."""
    validate_password_strength(plain_password)
    encoded = plain_password.encode("utf-8")
    return bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a password with a bcrypt hash without leaking parser failures."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("ascii"))
    except (ValueError, TypeError, UnicodeError):
        return False
