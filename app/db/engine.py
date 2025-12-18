from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.sqlalchemy_database_url(),
        pool_pre_ping=True,
    )


async def dispose_engine() -> None:
    if get_engine.cache_info().currsize == 0:
        return
    await get_engine().dispose()
