"""Operational endpoints nằm ngoài business API prefix."""

from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from src.application.health.i_health_service import IHealthService
from src.presentation.dependencies.health import get_health_service
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.health import HealthResponse, LivenessResponse, ReadinessResponse
from src.presentation.dtos.health.response import DatabaseHealthResponse
from src.presentation.routing import ApiResponseRoute

router = APIRouter(route_class=ApiResponseRoute)
HealthDependency = Annotated[IHealthService, Depends(get_health_service)]


@router.get("/", include_in_schema=False)
async def root_docs_redirect() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=HTTPStatus.TEMPORARY_REDIRECT)


@router.get("/health/live", response_model=LivenessResponse, tags=["Health Check"])
async def liveness_check() -> LivenessResponse:
    return LivenessResponse(timestamp=datetime.now(UTC))


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    tags=["Health Check"],
    responses={503: {"model": ApiErrorResponse}},
)
async def readiness_check(service: HealthDependency) -> ReadinessResponse | JSONResponse:
    output = await service.check()
    if output.database.status == "unhealthy":
        error = ApiErrorResponse(
            code=HTTPStatus.SERVICE_UNAVAILABLE,
            message="Database dependency is not ready.",
            error_code="SERVICE_UNAVAILABLE",
        )
        return JSONResponse(error.model_dump(mode="json"), status_code=error.code)
    return ReadinessResponse(
        timestamp=datetime.now(UTC),
        database=DatabaseHealthResponse.model_validate(
            output.database, from_attributes=True
        ),
    )


@router.get("/health", response_model=HealthResponse, tags=["Health Check"])
async def health_check(service: HealthDependency) -> HealthResponse:
    output = await service.check()
    return HealthResponse.from_application(output, datetime.now(UTC))
