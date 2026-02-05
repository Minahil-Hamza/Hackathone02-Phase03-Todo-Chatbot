"""Database session dependency for FastAPI."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import async_session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.

    Yields:
        AsyncSession: Database session for the current request.

    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
