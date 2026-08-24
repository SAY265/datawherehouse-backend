import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from config import Settings, get_settings
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from src.common.exceptions import register_exception_handlers
from src.common.logging import configure_logging, get_logger
from src.common.middleware import (
    HTTPLoggingMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    setup_cors_middleware,
)
from src.infrastructure.database.config import get_async_db_engine
from src.infrastructure.database.init_db import init_db
from src.infrastructure.llm.factory import LLMFactory
from src.presentation.api.router import router as api_router
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.health import (
    HealthResponse,
    LivenessResponse,
    ReadinessResponse,
)
from src.presentation.routing import ApiResponseRoute

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Quản lý vòng đời khởi chạy và dừng ứng dụng."""
    settings: Settings = get_settings()
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)

    # 1. Gọi hàm init_db() để khởi tạo CSDL
    try:
        await init_db(settings)
    except Exception as exc:
        logger.warning("Không thể khởi tạo CSDL lúc startup: %s", exc)

    yield
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """Khởi tạo và cấu hình ứng dụng FastAPI."""
    settings: Settings = get_settings()

    # 1. Cấu hình hệ thống Logging tập trung toàn dự án
    configure_logging(settings)

    app: FastAPI = FastAPI(
        title=settings.app_name,
        description="AI20K Agent System API",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.router.route_class = ApiResponseRoute

    # 2. Đăng ký Middleware Layer theo thứ tự thực thi (Innermost -> Outermost)
    # Innermost: HTTP Logging Middleware (Ghi nhận duration và log request lifecycle)
    app.add_middleware(HTTPLoggingMiddleware)

    # Context: Request ID Middleware (Thiết lập ContextVar và X-Request-ID response header)
    app.add_middleware(RequestIDMiddleware)

    # CORS Middleware Configuration
    setup_cors_middleware(app, settings)

    @app.middleware("http")
    async def normalize_prefix_middleware(request, call_next):
        if request.scope.get("path", "").startswith("/api/v1/api/v1/"):
            request.scope["path"] = request.scope["path"].replace("/api/v1/api/v1/", "/api/v1/", 1)
        return await call_next(request)

    # Outermost: Security Headers Middleware (Bổ sung Security Headers)
    if settings.security_headers_enabled:
        app.add_middleware(
            SecurityHeadersMiddleware,
            enable_hsts=settings.security_hsts_enabled,
        )

    # Trusted Host Validation (Nếu được kích hoạt)
    if settings.trusted_host_enabled:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts_list,
        )

    # 3. Đăng ký hệ thống xử lý ngoại lệ tập trung (Global Exception Handlers)
    register_exception_handlers(app)

    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        """Tự động chuyển hướng từ trang gốc sang Swagger Docs."""
        return RedirectResponse(url="/docs")

    async def _check_database_health() -> dict[str, Any]:
        """Kiểm tra tình trạng kết nối CSDL PostgreSQL trong giới hạn thời gian."""
        start_time = time.perf_counter()
        try:
            engine = get_async_db_engine()

            async def _ping_db():
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))

            await asyncio.wait_for(_ping_db(), timeout=2.0)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {"status": "healthy", "latency_ms": latency_ms}
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {"status": "unhealthy", "latency_ms": latency_ms, "error": str(exc)}

    def _check_llm_health() -> dict[str, Any]:
        """Kiểm tra cấu hình LLM Gateway."""
        effective_key = settings.openrouter_api_key or settings.openai_api_key
        is_configured = LLMFactory.is_api_key_valid(effective_key, settings.openai_base_url)
        provider = (
            "Local (Ollama/LMStudio)"
            if LLMFactory.is_local_provider(effective_key, settings.openai_base_url)
            else "Cloud Provider"
        )
        return {
            "status": "configured" if is_configured else "unconfigured",
            "provider_type": provider,
            "model": settings.model_name,
        }

    @app.get(
        "/health",
        tags=["Health Check"],
        response_model=HealthResponse,
        operation_id="healthCheck",
        responses={500: {"model": ApiErrorResponse}},
    )
    async def health_check() -> HealthResponse:
        """Endpoint kiểm tra trạng thái hoạt động tổng hợp (Deep Health Check)."""
        db_health = await _check_database_health()
        llm_health = _check_llm_health()

        return HealthResponse(
            status="ok",
            env=settings.app_env,
            timestamp=datetime.now(UTC).isoformat(),
            version="1.0.0",
            components={
                "database": db_health,
                "llm": llm_health,
            },
        )

    @app.get(
        "/health/live",
        tags=["Health Check"],
        response_model=LivenessResponse,
        operation_id="livenessCheck",
    )
    async def liveness_check() -> LivenessResponse:
        """Liveness Probe: Kiểm tra tiến trình FastAPI server còn phản hồi."""
        return LivenessResponse(
            status="ok",
            timestamp=datetime.now(UTC).isoformat(),
        )

    @app.get(
        "/health/ready",
        tags=["Health Check"],
        response_model=ReadinessResponse,
        operation_id="readinessCheck",
        responses={503: {"model": ApiErrorResponse}},
    )
    async def readiness_check() -> ReadinessResponse | JSONResponse:
        """Readiness Probe: Kiểm tra tính sẵn sàng phục vụ của toàn bộ phụ thuộc."""
        db_health = await _check_database_health()
        llm_health = _check_llm_health()
        is_ready = db_health["status"] == "healthy"

        components = {
            "database": db_health,
            "llm": llm_health,
        }

        if not is_ready:
            return JSONResponse(
                status_code=503,
                content={
                    "code": 503,
                    "message": "Service unavailable: Database dependency is not ready.",
                    "error_code": "DATABASE_ERROR",
                    "details": components,
                },
            )

        return ReadinessResponse(
            status="ready",
            components=components,
            timestamp=datetime.now(UTC).isoformat(),
        )

    return app


app: FastAPI = create_app()

if __name__ == "__main__":
    import uvicorn

    settings_env: Settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings_env.app_host,
        port=settings_env.app_port,
        reload=(settings_env.app_env == "development"),
    )
