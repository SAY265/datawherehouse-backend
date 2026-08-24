"""Router tổng hợp cho API phiên bản v1."""

from fastapi import APIRouter
from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.data_models import router as data_models_router
from src.presentation.api.v1.projects import router as projects_router
from src.presentation.api.v1.sandbox import router as sandbox_router
from src.presentation.api.v1.sessions import router as sessions_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(data_models_router)
router.include_router(sandbox_router)
router.include_router(sessions_router)
