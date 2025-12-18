from sqlalchemy import text

from app.db.engine import get_engine


async def check_db() -> None:
    engine = get_engine()
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

