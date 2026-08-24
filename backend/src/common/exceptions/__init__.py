"""Module cung cấp hệ thống Exception Handling cho ứng dụng."""

from src.common.exceptions.base import AppException
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.handler import register_exception_handlers
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.exceptions.system import SystemException

__all__: list[str] = [
    "AppException",
    "BusinessException",
    "SystemException",
    "InfrastructureException",
    "ErrorCode",
    "register_exception_handlers",
]
