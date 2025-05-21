import os
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database.connection import get_db
from app.core.database.migrations import create_tables, drop_tables
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/test_chat_db"
)

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db() -> AsyncGenerator:
    """Create test database and tables."""
    async with test_engine.begin() as conn:
        await create_tables()
    yield
    async with test_engine.begin() as conn:
        await drop_tables()

@pytest_asyncio.fixture
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for a test."""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(db_session) -> AsyncGenerator[User, None]:
    """Create a test user."""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    user = await user_service.create_user(user_data)
    yield user
    await db_session.delete(user)
    await db_session.commit() 