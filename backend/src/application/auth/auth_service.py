"""Authentication application service."""

from src.application.auth.i_auth_service import IAuthService
from src.application.auth.input import LoginInput, RegisterInput
from src.application.auth.output import AuthTokenOutput, UserOutput
from src.application.common.unit_of_work import IUnitOfWork
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.types import EntityID
from src.domain.user.entities import User
from src.domain.user.repository import IUserRepository
from src.domain.user.value_objects import Email
from src.infrastructure.security.jwt import create_access_token, revoke_access_token
from src.infrastructure.security.password import hash_password, verify_password
from typing_extensions import override

# A valid hash used only to equalize the missing-user login path.
_DUMMY_PASSWORD_HASH = "$2b$12$JqZ2l9gM.w0gAj6dfsaG5uW7P2CqD.Ff7iH4dBGoA3TZ1CzpRXZtW"


class AuthService(IAuthService):
    """Register, authenticate, and safely expose user profiles."""

    def __init__(self, user_repository: IUserRepository, unit_of_work: IUnitOfWork) -> None:
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work

    @override
    async def register(self, data: RegisterInput) -> AuthTokenOutput:
        username = data.username.strip().lower()
        email = Email(data.email).value

        if await self._user_repository.get_by_username(username) is not None:
            raise BusinessException(
                code=ErrorCode.INVALID_USERNAME,
                message="Tên đăng nhập đã được sử dụng.",
            )
        if await self._user_repository.get_by_email(email) is not None:
            raise BusinessException(
                code=ErrorCode.INVALID_EMAIL,
                message="Địa chỉ email đã được sử dụng.",
            )
        try:
            hashed_password = hash_password(data.password)
        except ValueError as exc:
            raise BusinessException(
                code=ErrorCode.INVALID_PASSWORD,
                message=str(exc),
            ) from exc

        user = await self._user_repository.save(
            User(
                username=username,
                email=Email(email),
                hashed_password=hashed_password,
                full_name=data.full_name,
            )
        )
        await self._unit_of_work.commit()
        return self._token_output(user)

    @override
    async def login(self, data: LoginInput) -> AuthTokenOutput:
        identifier = data.identifier.strip().lower()
        if "@" in identifier:
            user = await self._user_repository.get_by_email(identifier)
        else:
            user = await self._user_repository.get_by_username(identifier)

        password_hash = user.hashed_password if user is not None else _DUMMY_PASSWORD_HASH
        password_matches = verify_password(data.password, password_hash)
        if user is None or not password_matches or not user.is_active:
            raise BusinessException(
                code=ErrorCode.INVALID_CREDENTIALS,
                message="Tên đăng nhập/email hoặc mật khẩu không chính xác.",
            )
        return self._token_output(user)

    @override
    async def get_current_user(self, user_id: EntityID) -> UserOutput:
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise BusinessException(
                code=ErrorCode.USER_NOT_FOUND,
                message="Không tìm thấy tài khoản.",
            )
        return UserOutput.from_domain(user)

    @override
    async def logout(self, access_token: str) -> None:
        revoke_access_token(access_token)

    @staticmethod
    def _token_output(user: User) -> AuthTokenOutput:
        return AuthTokenOutput(
            access_token=create_access_token(str(user.id)),
            token_type="bearer",
            user=UserOutput.from_domain(user),
        )
