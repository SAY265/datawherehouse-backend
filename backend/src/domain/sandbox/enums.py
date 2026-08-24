"""Định nghĩa các Enum cho miền Sandbox."""

from enum import StrEnum


class SandboxDbType(StrEnum):
    """Loại cơ sở dữ liệu Sandbox."""

    POSTGRESQL = "POSTGRESQL"
    BIGQUERY = "BIGQUERY"
    SNOWFLAKE = "SNOWFLAKE"
    MYSQL = "MYSQL"
    SQLITE = "SQLITE"
