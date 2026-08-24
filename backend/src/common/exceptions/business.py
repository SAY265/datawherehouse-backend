"""Ngoại lệ dành cho các lỗi logic nghiệp vụ (Business Logic Errors)."""

from src.common.exceptions.base import AppException


class BusinessException(AppException):
    """Ngoại lệ chung đại diện cho các lỗi nghiệp vụ trong hệ thống.

    Được ném ra từ tầng Domain hoặc Application khi có vi phạm quy tắc nghiệp vụ.
    """

    pass
