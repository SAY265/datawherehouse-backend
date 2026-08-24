"""Cấu hình khởi tạo và quản lý kết nối CSDL PostgreSQL (Engine & Database URLs)."""

from functools import lru_cache

from config import Settings, get_settings
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def get_async_database_url(settings: Settings | None = None) -> str:
    """Tạo chuỗi URL kết nối bất đồng bộ PostgreSQL (postgresql+asyncpg://)."""
    app_settings: Settings = settings or get_settings()
    if app_settings.database_url and "asyncpg" in app_settings.database_url:
        return app_settings.database_url
    if app_settings.database_url and app_settings.database_url.startswith("postgresql://"):
        return app_settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    return (
        f"postgresql+asyncpg://{app_settings.postgres_user}:{app_settings.postgres_password}"
        f"@{app_settings.postgres_host}:{app_settings.postgres_port}/{app_settings.postgres_db}"
    )


def get_sync_database_url(settings: Settings | None = None) -> str:
    """Tạo chuỗi URL kết nối đồng bộ PostgreSQL (postgresql+psycopg2://)."""
    app_settings: Settings = settings or get_settings()
    if app_settings.database_url and "psycopg2" in app_settings.database_url:
        return app_settings.database_url
    if app_settings.database_url and app_settings.database_url.startswith("postgresql+asyncpg://"):
        return app_settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if app_settings.database_url and app_settings.database_url.startswith("postgresql://"):
        return app_settings.database_url.replace("postgresql://", "postgresql+psycopg2://")
    return (
        f"postgresql+psycopg2://{app_settings.postgres_user}:{app_settings.postgres_password}"
        f"@{app_settings.postgres_host}:{app_settings.postgres_port}/{app_settings.postgres_db}"
    )


@lru_cache
def get_async_db_engine(settings: Settings | None = None) -> AsyncEngine:
    """Tạo hoặc lấy AsyncEngine kết nối bất đồng bộ PostgreSQL."""
    app_settings: Settings = settings or get_settings()
    url: str = get_async_database_url(app_settings)
    connect_args = {"timeout": 3, "command_timeout": 5} if "asyncpg" in url else {}
    return create_async_engine(
        url,
        echo=(app_settings.app_env == "development"),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args=connect_args,
    )


@lru_cache
def get_sync_db_engine(settings: Settings | None = None) -> Engine:
    """Tạo hoặc lấy Engine kết nối đồng bộ PostgreSQL."""
    app_settings: Settings = settings or get_settings()
    url: str = get_sync_database_url(app_settings)
    return create_engine(
        url,
        echo=(app_settings.app_env == "development"),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
