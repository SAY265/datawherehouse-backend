"""FastAPI dependency wiring for authentication."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.auth.auth_service import AuthService
from src.application.auth.i_auth_service import IAuthService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.user.entities import User
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from src.infrastructure.security.authentication import BearerCredentials, bearer_scheme
from src.infrastructure.security.jwt import (
    AccessTokenError,
    AccessTokenExpiredError,
    decode_access_token,
)
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_auth_service(session: AsyncSession = Depends(get_async_db_session)) -> IAuthService:
    return AuthService(
        user_repository=PostgresUserRepository(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )


async def get_current_user(
    credentials: Annotated[BearerCredentials | None, Depends(bearer_scheme)],
    session: AsyncSession = Depends(get_async_db_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_REQUIRED,
            message="Vui lòng đăng nhập để tiếp tục.",
        )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except AccessTokenExpiredError as exc:
        raise BusinessException(
            code=ErrorCode.TOKEN_EXPIRED,
            message="Phiên đăng nhập đã hết hạn.",
        ) from exc
    except (AccessTokenError, ValueError, TypeError, KeyError) as exc:
        raise BusinessException(
            code=ErrorCode.TOKEN_INVALID,
            message="Phiên đăng nhập không hợp lệ.",
        ) from exc

    user = await PostgresUserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise BusinessException(
            code=ErrorCode.INVALID_CREDENTIALS,
            message="Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.",
        )
    return user


AuthServiceDependency = Annotated[IAuthService, Depends(get_auth_service)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
BearerCredentialsDependency = Annotated[BearerCredentials | None, Depends(bearer_scheme)]
