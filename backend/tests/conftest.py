"""Shared test fixtures for the AI Todo Chatbot backend tests."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from src.main import app
from src.db.session import get_session


# Create test database engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    echo=False,
    future=True,
)

# Test session factory
test_session_factory = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session
    async with test_session_factory() as session:
        yield session

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_session dependency for tests."""
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing the API."""
    # Override the session dependency
    app.dependency_overrides[get_session] = override_get_session

    # Create tables for this test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def test_user_data() -> dict:
    """Return test user registration data."""
    return {
        "email": "test@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def test_user_data_2() -> dict:
    """Return second test user registration data."""
    return {
        "email": "test2@example.com",
        "password": "anotherpassword456",
    }
