from typing import Any, AsyncGenerator
from unittest.mock import MagicMock

import pytest
from fakeredis.aioredis import FakeRedis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import forum.auth.models  # noqa: F401
from forum.auth.schemas import UserCreate
import forum.forum.models  # noqa: F401
import forum.post.models  # noqa: F401
import forum.thread.models  # noqa: F401
from forum.auth.models import Role, User, hash_password
from forum.database.core import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
VALID_USERNAME = "Testuser"
VALID_PASSWORD = "Testpassword123"
HASHED_VALID_PASSWORD = hash_password(VALID_PASSWORD)
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
async def test_redis():
    return FakeRedis(decode_responses=True)


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


@pytest.fixture
def mock_response():
    return MagicMock()


@pytest.fixture
async def test_user_role(test_session) -> Role:
    role = Role(id=1, name="User")
    test_session.add(role)
    await test_session.flush()
    return role


@pytest.fixture
async def test_mod_role(test_session) -> Role:
    role = Role(id=2, name="Moderator")
    test_session.add(role)
    await test_session.flush()
    return role


@pytest.fixture
async def test_adm_role(test_session) -> Role:
    role = Role(id=3, name="Admin")
    test_session.add(role)
    await test_session.flush()
    return role


@pytest.fixture
def valid_user(user_data) -> UserCreate:
    return UserCreate(**user_data)


@pytest.fixture
async def test_user(test_session, test_user_role):
    u = User(
        username=VALID_USERNAME,
        email=VALID_EMAIL,
        password=HASHED_VALID_PASSWORD,
        role=test_user_role,
    )
    test_session.add(u)
    await test_session.flush()
    return u


@pytest.fixture
async def test_user2(test_session):
    u = User(
        username=VALID_USERNAME + "2",
        email=VALID_EMAIL.replace("user", "user2"),
        password=VALID_PASSWORD.encode(),
    )
    test_session.add(u)
    await test_session.flush()
    return u


@pytest.fixture
async def test_mod(test_session, test_mod_role):
    u = User(
        username="moderator",
        email="moderator@example.com",
        password=VALID_PASSWORD,
        role=test_mod_role,
    )
    test_session.add(u)
    await test_session.flush()
    return u


@pytest.fixture
async def test_adm(test_session, test_adm_role):
    u = User(
        username="admin",
        email="admin@example.com",
        password=VALID_PASSWORD,
        role=test_adm_role,
    )
    test_session.add(u)
    await test_session.flush()
    return u
