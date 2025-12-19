from app.api.routers.projects import router as projects_router
from app.api.routers.music import router as music_router
from app.api.routers.layers import router as layers_router
from app.api.routers.keyframes import router as keyframes_router
from app.api.routers.assets import router as assets_router

__all__ = [
    "projects_router",
    "music_router",
    "layers_router",
    "keyframes_router",
    "assets_router",
]

