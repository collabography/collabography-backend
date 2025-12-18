from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.engine import dispose_engine


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await dispose_engine()

    app = FastAPI(title="collabography-backend", lifespan=lifespan)
    app.include_router(api_router)
    return app


app = create_app()
