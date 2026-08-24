"""Authentication API endpoints."""

from fastapi import APIRouter
from src.application.auth.output import UserOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.presentation.dependencies.auth import (
    AuthServiceDependency,
    BearerCredentialsDependency,
    CurrentUserDependency,
)
from src.presentation.dtos.auth.request import LoginRequest, RegisterRequest
from src.presentation.dtos.auth.response import AuthTokenResponse, LogoutResponse, UserResponse
from src.presentation.routing import ApiResponseRoute

router = APIRouter(prefix="/auth", tags=["Authentication"], route_class=ApiResponseRoute)


@router.post("/register", response_model=AuthTokenResponse, operation_id="register")
async def register(request: RegisterRequest, service: AuthServiceDependency) -> AuthTokenResponse:
    return AuthTokenResponse.from_application(await service.register(request.to_application()))


@router.post("/login", response_model=AuthTokenResponse, operation_id="login")
async def login(request: LoginRequest, service: AuthServiceDependency) -> AuthTokenResponse:
    return AuthTokenResponse.from_application(await service.login(request.to_application()))


@router.get("/me", response_model=UserResponse, operation_id="getCurrentUser")
async def me(current_user: CurrentUserDependency) -> UserResponse:
    return UserResponse.from_application(UserOutput.from_domain(current_user))


@router.post("/logout", response_model=LogoutResponse, operation_id="logout")
async def logout(
    current_user: CurrentUserDependency,
    credentials: BearerCredentialsDependency,
    service: AuthServiceDependency,
) -> LogoutResponse:
    del current_user
    if credentials is None:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_REQUIRED,
            message="Vui lòng đăng nhập để tiếp tục.",
        )
    await service.logout(credentials.credentials)
    return LogoutResponse()
