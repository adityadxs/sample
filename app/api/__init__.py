"""API routers package."""
from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.skus import router as skus_router
from app.api.predict import router as predict_router
from app.api.feedback import router as feedback_router
from app.api.models import router as models_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(skus_router)
api_router.include_router(predict_router)
api_router.include_router(feedback_router)
api_router.include_router(models_router)

__all__ = ["api_router"]
