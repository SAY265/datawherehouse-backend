"""Ngoại lệ dành cho các lỗi kỹ thuật và hệ thống (System & Technical Errors)."""

from src.common.exceptions.base import AppException


class SystemException(AppException):
    """Ngoại lệ chung đại diện cho các lỗi kỹ thuật hoặc hạ tầng hệ thống.

    Được ném ra từ tầng Infrastructure hoặc System services khi xảy ra sự cố kỹ thuật
    (DB failure, LLM connection failure, Redis down, External API error...).
    """

    pass
