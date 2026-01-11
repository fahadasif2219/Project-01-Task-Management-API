"""Pytest fixtures for testing."""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Set test database URL before importing app modules
os.environ["NEON_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.core.database import get_session


# Create test engine and session
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)

test_async_session = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_session():
    """Get test database session."""
    async with test_async_session() as session:
        yield session


@pytest.fixture
async def setup_db():
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client(setup_db):
    """Get test client."""
    app.dependency_overrides[get_session] = get_test_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
