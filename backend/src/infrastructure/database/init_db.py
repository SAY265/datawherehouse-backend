"""Script tự động kiểm tra và khởi tạo các bảng CSDL cho hệ thống."""

import asyncio

import src.infrastructure.database.models  # noqa: F401
from config import Settings, get_settings
from sqlalchemy import text
from src.common.logging import get_logger
from src.infrastructure.database.base import Base
from src.infrastructure.database.config import get_async_db_engine

logger = get_logger(__name__)

_DEVELOPMENT_SCHEMA_MIGRATIONS = (
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255) NOT NULL DEFAULT ''",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(150)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'USER'",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_normalized ON users (LOWER(email))",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_normalized ON users (LOWER(username))",
)


async def init_db(settings: Settings | None = None) -> None:
    """Kiểm tra và tự động khởi tạo/cập nhật cấu trúc bảng CSDL nếu ở môi trường development."""
    app_settings = settings or get_settings()

    if app_settings.app_env != "development":
        logger.info("Bỏ qua tự động sync schema CSDL ở môi trường %s", app_settings.app_env)
        return

    logger.info("Kiểm tra kết nối CSDL và đồng bộ schema các bảng ở môi trường development...")
    try:
        engine = get_async_db_engine()

        async def _create_tables():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # create_all không ALTER bảng đã tồn tại. Các lệnh idempotent này
                # giữ database development cũ tương thích với luồng tài khoản.
                for statement in _DEVELOPMENT_SCHEMA_MIGRATIONS:
                    await conn.execute(text(statement))

        await asyncio.wait_for(_create_tables(), timeout=5.0)
        logger.info("CSDL đã được khởi tạo và đồng bộ bảng thành công!")
    except Exception as exc:
        logger.warning("Không thể đồng bộ schema CSDL lúc khởi động (tiếp tục chạy service): %s", exc)


if __name__ == "__main__":
    asyncio.run(init_db())
