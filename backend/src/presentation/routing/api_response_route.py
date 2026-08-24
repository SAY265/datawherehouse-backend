"""FastAPI route tự động bọc success payload bằng response envelope chuẩn."""

from collections.abc import Awaitable, Callable
from functools import wraps
from http import HTTPStatus
from inspect import iscoroutinefunction
from typing import cast

from fastapi.datastructures import DefaultPlaceholder
from fastapi.routing import APIRoute
from src.common.dto.response import ApiResponse
from starlette.responses import Response
from typing_extensions import override

Endpoint = Callable[..., object]
AsyncEndpoint = Callable[..., Awaitable[object]]


class ApiResponseRoute(APIRoute):
    """Bọc payload và biến response model thành `ApiResponse[payload]`."""

    @override
    def __init__(
        self,
        path: str,
        endpoint: Endpoint,
        **kwargs: object,
    ) -> None:
        """Cấu hình runtime response và OpenAPI schema từ một payload model."""
        response_model = kwargs.get("response_model")
        if _has_payload_model(response_model):
            kwargs["response_model"] = ApiResponse[response_model]
            status_code = cast(int | None, kwargs.get("status_code"))
            endpoint = _wrap_endpoint(endpoint, status_code)
        super().__init__(path=path, endpoint=endpoint, **kwargs)


def _has_payload_model(response_model: object) -> bool:
    """Chỉ bọc route khai báo payload model tường minh."""
    return response_model is not None and not isinstance(response_model, DefaultPlaceholder)


def _wrap_endpoint(endpoint: Endpoint, status_code: int | None) -> Endpoint:
    """Bọc cả async và sync endpoint mà vẫn giữ nguyên chữ ký FastAPI đọc được."""
    if iscoroutinefunction(endpoint):
        async_endpoint = cast(AsyncEndpoint, endpoint)

        @wraps(endpoint)
        async def async_wrapper(*args: object, **kwargs: object) -> object:
            payload = await async_endpoint(*args, **kwargs)
            return _to_envelope(payload, status_code)

        return async_wrapper

    @wraps(endpoint)
    def sync_wrapper(*args: object, **kwargs: object) -> object:
        return _to_envelope(endpoint(*args, **kwargs), status_code)

    return sync_wrapper


def _to_envelope(payload: object, status_code: int | None) -> object:
    """Chuyển payload thành success envelope, trừ raw Response đặc biệt."""
    if isinstance(payload, (Response, ApiResponse)):
        return payload
    code = status_code or HTTPStatus.OK.value
    return ApiResponse[object](code=code, data=payload)
