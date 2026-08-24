"""HS256 JWT adapter với claim validation nghiêm ngặt."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from src.application.auth.i_auth_service import ITokenCodec
from src.application.auth.token_models import IssuedToken, TokenClaims
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import utc_now
from src.domain.shared.types import EntityID
from typing_extensions import override

ALGORITHM = "HS256"


class JwtTokenCodec(ITokenCodec):
    """Issue and strictly validate HS256 access tokens."""

    def __init__(self, secret: str, expires_minutes: int) -> None:
        if not secret.strip():
            raise ValueError("SECRET_KEY không được để trống.")
        self._secret = secret
        self._expires_minutes = expires_minutes

    @override
    def issue(self, user_id: EntityID) -> IssuedToken:
        issued_at = utc_now()
        expires_at = issued_at + timedelta(minutes=self._expires_minutes)
        payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "iat": issued_at,
            "exp": expires_at,
            "type": "access",
        }
        return IssuedToken(jwt.encode(payload, self._secret, algorithm=ALGORITHM), expires_at)

    @override
    def decode(self, token: str) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[ALGORITHM],
                options={"require": ["sub", "jti", "iat", "exp", "type"]},
            )
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError("Unexpected token type")
            return TokenClaims(
                user_id=UUID(str(payload["sub"])),
                jti=str(payload["jti"]),
                issued_at=_timestamp(payload["iat"]),
                expires_at=_timestamp(payload["exp"]),
            )
        except jwt.ExpiredSignatureError as exc:
            raise BusinessException(ErrorCode.TOKEN_EXPIRED, "Token đã hết hạn.") from exc
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
            raise BusinessException(ErrorCode.TOKEN_INVALID, "Token không hợp lệ.") from exc


def _timestamp(value: object) -> datetime:
    if not isinstance(value, (int, float)):
        raise TypeError("JWT timestamp không hợp lệ.")
    return datetime.fromtimestamp(value, tz=UTC)
