"""Router gốc của application API."""

from fastapi import APIRouter
from src.presentation.api.v1.router import router as v1_router

router = APIRouter()
router.include_router(v1_router)
