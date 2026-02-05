"""Database configuration and session management."""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlmodel import SQLModel

# Load environment variables
load_dotenv()

# Database URL from environment - defaults to SQLite for easy local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./todo_chatbot.db")

# Determine if using SQLite
is_sqlite = DATABASE_URL.startswith("sqlite")

# Create async engine with appropriate settings
if is_sqlite:
    # SQLite configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("ENVIRONMENT", "development") == "development",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("ENVIRONMENT", "development") == "development",
        future=True,
        poolclass=NullPool,  # Disable connection pooling for serverless DB compatibility
    )

# Async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
