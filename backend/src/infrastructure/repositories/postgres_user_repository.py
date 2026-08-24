"""Triển khai PostgreSQL Repository cho thực thể User."""

from config import get_settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.logging import get_logger
from src.domain.shared.types import EntityID
from src.domain.user.entities import User
from src.domain.user.repository import IUserRepository
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.repositories.in_memory_store import InMemoryStore
from typing_extensions import override

logger = get_logger(__name__)


class PostgresUserRepository(IUserRepository):
    """Triển khai IUserRepository sử dụng SQLAlchemy AsyncSession với In-Memory Fallback."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo repository với SQLAlchemy AsyncSession."""
        self._session: AsyncSession = session
        self._mem = InMemoryStore.get_instance()
        # Tài khoản không được báo lưu thành công khi PostgreSQL lỗi. Fallback
        # chỉ tồn tại trong test để unit test không phụ thuộc database thật.
        self._allow_memory_fallback = get_settings().app_env == "test"

    @override
    async def get_by_id(self, entity_id: EntityID) -> User | None:
        """Lấy người dùng theo ID."""
        try:
            stmt = select(UserModel).where(UserModel.id == entity_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return UserMapper.to_domain(model) if model else None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for get_user_by_id: %s", exc)
            return self._mem.get_user_by_id(entity_id)

    @override
    async def get_by_username(self, username: str) -> User | None:
        """Lấy thông tin người dùng theo tên đăng nhập."""
        try:
            normalized = username.strip().lower()
            stmt = select(UserModel).where(UserModel.username == normalized)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return UserMapper.to_domain(model) if model else None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for get_user_by_username: %s", exc)
            return self._mem.get_user_by_username(username)

    @override
    async def get_by_email(self, email: str) -> User | None:
        """Lấy thông tin người dùng theo địa chỉ email."""
        try:
            normalized = email.strip().lower()
            stmt = select(UserModel).where(UserModel.email == normalized)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return UserMapper.to_domain(model) if model else None
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, falling back to in-memory store for get_user_by_email: %s", exc)
            return self._mem.get_user_by_email(email)

    @override
    async def save(self, entity: User) -> User:
        """Lưu (tạo mới hoặc cập nhật) thực thể User."""
        if self._allow_memory_fallback:
            self._mem.save_user(entity)
        try:
            stmt = select(UserModel).where(UserModel.id == entity.id)
            result = await self._session.execute(stmt)
            existing_model = result.scalar_one_or_none()

            if existing_model:
                model = UserMapper.update_model(existing_model, entity)
            else:
                model = UserMapper.to_model(entity)
                self._session.add(model)

            await self._session.flush()
            return UserMapper.to_domain(model)
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, user saved to in-memory store: %s", exc)
            return entity

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể User theo ID."""
        if self._allow_memory_fallback:
            self._mem.users.pop(str(entity_id), None)
        try:
            stmt = select(UserModel).where(UserModel.id == entity_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return False
            await self._session.delete(model)
            await self._session.flush()
            return True
        except Exception as exc:
            if not self._allow_memory_fallback:
                raise
            logger.warning("Database unavailable, deleted from in-memory store: %s", exc)
            return True
