"""Creation, verification, and process-local revocation of access tokens."""

from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any
from uuid import uuid4

import jwt
from config import Settings, get_settings


class AccessTokenError(ValueError):
    """Base error for access-token validation failures."""


class AccessTokenExpiredError(AccessTokenError):
    """Raised when a correctly signed token has expired."""


_revoked_tokens: dict[str, datetime] = {}
_revocation_lock = Lock()


def _settings(settings: Settings | None) -> Settings:
    return settings or get_settings()


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    *,
    settings: Settings | None = None,
) -> str:
    """Create a short-lived HS256 JWT containing only non-sensitive claims."""
    app_settings = _settings(settings)
    issued_at = datetime.now(UTC)
    expires_at = issued_at + (expires_delta or timedelta(minutes=app_settings.access_token_expire_minutes))
    payload = {
        "sub": str(subject),
        "iat": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, app_settings.secret_key, algorithm="HS256")


def decode_access_token(token: str, *, settings: Settings | None = None) -> dict[str, Any]:
    """Verify signature, required claims, token type, and logout revocation state."""
    app_settings = _settings(settings)
    try:
        payload = jwt.decode(
            token,
            app_settings.secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "exp", "iat", "jti", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AccessTokenExpiredError("Access token has expired.") from exc
    except jwt.PyJWTError as exc:
        raise AccessTokenError("Access token is invalid.") from exc

    if payload.get("type") != "access" or not isinstance(payload.get("sub"), str):
        raise AccessTokenError("Access token has invalid claims.")
    if _is_revoked(str(payload["jti"])):
        raise AccessTokenError("Access token has been revoked.")
    return payload


def revoke_access_token(token: str, *, settings: Settings | None = None) -> None:
    """Deny a token for the remainder of its lifetime after logout."""
    payload = decode_access_token(token, settings=settings)
    expiration = datetime.fromtimestamp(float(payload["exp"]), tz=UTC)
    with _revocation_lock:
        _purge_expired_revocations(datetime.now(UTC))
        _revoked_tokens[str(payload["jti"])] = expiration


def _is_revoked(jti: str) -> bool:
    now = datetime.now(UTC)
    with _revocation_lock:
        _purge_expired_revocations(now)
        return jti in _revoked_tokens


def _purge_expired_revocations(now: datetime) -> None:
    expired = [jti for jti, expires_at in _revoked_tokens.items() if expires_at <= now]
    for jti in expired:
        _revoked_tokens.pop(jti, None)
