"""Factory duy nhất cho OpenAPI error responses chuẩn."""

from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.routing.types import ErrorResponses


def error_responses(*statuses: int) -> ErrorResponses:
    """Tạo mapping error envelope thống nhất cho các HTTP status đã khai báo."""
    return {status: {"model": ApiErrorResponse} for status in statuses}
