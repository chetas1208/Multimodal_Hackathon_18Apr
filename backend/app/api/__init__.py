from fastapi import APIRouter

from app.api.activity import router as activity_router
from app.api.analytics import router as analytics_router
from app.api.assets import router as assets_router
from app.api.bot import router as bot_router
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(assets_router)
api_router.include_router(analytics_router)
api_router.include_router(bot_router)
api_router.include_router(upload_router)
api_router.include_router(activity_router)
