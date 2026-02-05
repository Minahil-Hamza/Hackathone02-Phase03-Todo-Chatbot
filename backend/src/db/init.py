"""Database initialization script."""

import asyncio
import logging
from src.db import init_db, close_db

# Import models to register them with SQLModel
from src.models import Task, Conversation, Message, User, RefreshToken  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize the database tables."""
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialized successfully!")
        logger.info("Tables created: tasks, conversations, messages, users, refresh_tokens")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
