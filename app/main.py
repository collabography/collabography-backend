from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.engine import dispose_engine


tags_metadata = [
    {
        "name": "health",
        "description": "서비스 및 데이터베이스 상태 확인용 엔드포인트",
    },
]


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await dispose_engine()

    app = FastAPI(
        title="collabography-backend",
        description="collabography 서비스용 백엔드 API 문서입니다.",
        version="0.1.0",
        openapi_tags=tags_metadata,
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc 문서
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
