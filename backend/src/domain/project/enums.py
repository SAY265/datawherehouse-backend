"""Các kiểu liệt kê (Enums) thuộc miền Dự án (Project)."""

from enum import StrEnum


class ProjectStatus(StrEnum):
    """Trạng thái hoạt động của Dự án."""

    ACTIVE = "ACTIVE"
    ANALYZING = "ANALYZING"
    ARCHIVED = "ARCHIVED"


class ProjectRole(StrEnum):
    """Vai trò của thành viên trong Dự án."""

    OWNER = "OWNER"
    MEMBER = "MEMBER"
