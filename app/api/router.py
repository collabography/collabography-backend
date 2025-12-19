from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routers import (
    projects_router,
    music_router,
    layers_router,
    keyframes_router,
    assets_router,
)

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(projects_router)
api_router.include_router(music_router)
api_router.include_router(layers_router)
api_router.include_router(keyframes_router)
api_router.include_router(assets_router)

