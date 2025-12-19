from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async for session in get_session():
        yield session


def get_settings_dep() -> Settings:
    """Dependency for getting settings"""
    return get_settings()

