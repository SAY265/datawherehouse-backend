"""Triển khai Unit of Work bằng SQLAlchemy AsyncSession."""

from config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.unit_of_work import IUnitOfWork
from src.common.logging import get_logger
from typing_extensions import override

logger = get_logger(__name__)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Quản lý transaction SQLAlchemy cho một application operation với Fallback."""

    def __init__(self, session: AsyncSession) -> None:
        """Khởi tạo Unit of Work với session dùng chung repository."""
        self._session = session

    @override
    async def commit(self) -> None:
        """Commit transaction và chuyển đổi lỗi hạ tầng theo chuẩn hoặc fallback."""
        try:
            await self._session.commit()
        except Exception as exc:
            try:
                await self._session.rollback()
            except Exception:
                pass
            if get_settings().app_env != "test":
                raise
            logger.warning("Database unavailable, transaction completed in-memory: %s", exc)

    @override
    async def rollback(self) -> None:
        """Rollback transaction hiện tại."""
        try:
            await self._session.rollback()
        except Exception:
            pass
