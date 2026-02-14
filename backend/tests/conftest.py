from typing import Any, AsyncGenerator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from forum.database.core import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
VALID_USERNAME = "Testuser"
VALID_PASSWORD = "Testpassword123"
VALID_EMAIL = "testuser@email.com"


@pytest.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    sessionlocal = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with sessionlocal() as session:
        yield session


@pytest.fixture
def user_data() -> dict[str, Any]:
    return {
        "username": VALID_USERNAME,
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD,
    }


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.app = MagicMock()
    request.app.state = MagicMock()
    return request
