"""Bộ xử lý ngoại lệ toàn cục (Global Exception Handler) cho ứng dụng FastAPI."""

import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.common.exceptions.base import AppException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.error_status import get_http_status_code
from src.common.logging import get_logger
from starlette.exceptions import HTTPException as StarletteHTTPException

logger: logging.Logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Xử lý các ngoại lệ kế thừa từ AppException (BusinessException & SystemException)."""
    status: HTTPStatus = get_http_status_code(exc.code)
    status_code: int = status.value

    # Ghi log tương ứng với mức độ lỗi
    if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.error(
            "SystemException [%s] (%d) tại path %s: %s",
            exc.code,
            status_code,
            request.url.path,
            exc.message,
            exc_info=True,
        )
    else:
        logger.info(
            "BusinessException [%s] (%d) tại path %s: %s",
            exc.code,
            status_code,
            request.url.path,
            exc.message,
        )

    content: dict[str, Any] = {
        "code": status_code,
        "message": exc.message,
        "error_code": exc.code.value,
        "details": exc.details,
    }
    return JSONResponse(status_code=status_code, content=content)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Xử lý lỗi validation dữ liệu đầu vào từ Pydantic / FastAPI."""
    status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY.value
    details: list[dict[str, str]] = []

    for err in exc.errors():
        loc: list[str] = [str(x) for x in err.get("loc", []) if x != "body"]
        field_name: str = ".".join(loc) if loc else "payload"
        details.append(
            {
                "field": field_name,
                "message": err.get("msg", "Dữ liệu không hợp lệ"),
            }
        )

    logger.warning(
        "Validation error tại path %s: %s",
        request.url.path,
        details,
    )

    content: dict[str, Any] = {
        "code": status_code,
        "message": "Request validation failed.",
        "error_code": ErrorCode.VALIDATION_ERROR.value,
        "details": details,
    }
    return JSONResponse(status_code=status_code, content=content)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Xử lý các ngoại lệ dạng Starlette / FastAPI HTTPException."""
    status_code: int = exc.status_code
    message: str = str(exc.detail) if exc.detail else "HTTP Exception"

    # Ánh xạ sơ bộ status code sang ErrorCode phù hợp
    error_code_str: str = ErrorCode.INTERNAL_SERVER_ERROR.value
    if status_code == HTTPStatus.NOT_FOUND:
        error_code_str = ErrorCode.RESOURCE_NOT_FOUND.value
    elif status_code == HTTPStatus.UNAUTHORIZED:
        error_code_str = ErrorCode.AUTHENTICATION_REQUIRED.value
    elif status_code == HTTPStatus.FORBIDDEN:
        error_code_str = ErrorCode.PERMISSION_DENIED.value
    elif status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        error_code_str = ErrorCode.VALIDATION_ERROR.value

    content: dict[str, Any] = {
        "code": status_code,
        "message": message,
        "error_code": error_code_str,
        "details": None,
    }
    return JSONResponse(status_code=status_code, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Xử lý tất cả các ngoại lệ chưa được bắt (Unhandled / Unexpected Exceptions)."""
    logger.exception(
        "Lỗi không xác định (Unhandled Exception) tại path %s: %s",
        request.url.path,
        exc,
    )

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    content: dict[str, Any] = {
        "code": status_code,
        "message": "Internal server error.",
        "error_code": ErrorCode.INTERNAL_SERVER_ERROR.value,
        "details": None,
    }
    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký tất cả các exception handler vào FastAPI app instance."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
