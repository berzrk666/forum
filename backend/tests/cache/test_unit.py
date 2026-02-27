import pytest

from forum.auth.schemas import UserRead
from forum.cache.repository import RECENT_USERS_KEY, CacheRepository
from tests.conftest import VALID_USERNAME


@pytest.fixture
def cache_repo():
    return CacheRepository()


class TestCachePushRecentUser:
    async def test_push_to_empty_list(
        self, cache_repo: CacheRepository, test_redis, test_readuser
    ):
        """Recent list should contain only the newly added user."""
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await test_redis.lrange(RECENT_USERS_KEY, 0, -1)

        assert recent_users
        assert len(recent_users) == 1

    async def test_push_two_users(
        self, cache_repo: CacheRepository, test_redis, test_readuser
    ):
        """Recent list should contain the two newly added user in the correct order."""
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username2"
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await test_redis.lrange(RECENT_USERS_KEY, 0, -1)

        assert len(recent_users) == 2

        data = UserRead.model_validate_json(recent_users[0])
        assert data.username == "username2"
        data = UserRead.model_validate_json(recent_users[1])
        assert data.username == VALID_USERNAME

    async def test_push_exactly_max_recent_users(
        self, cache_repo: CacheRepository, test_redis, test_readuser, monkeypatch
    ):
        """Recent list should contain the exactly max number of recent users and in correct order."""
        monkeypatch.setattr("forum.cache.repository.LAST_N", 5)
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username2"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username3"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username4"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username5"
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await test_redis.lrange(RECENT_USERS_KEY, 0, -1)

        assert len(recent_users) == 5

        data = UserRead.model_validate_json(recent_users[0])
        assert data.username == "username5"
        data = UserRead.model_validate_json(recent_users[1])
        assert data.username == "username4"
        data = UserRead.model_validate_json(recent_users[4])
        assert data.username == VALID_USERNAME

    async def test_push_one_more_than_max(
        self, cache_repo: CacheRepository, test_redis, test_readuser, monkeypatch
    ):
        """Recent list should contain the max number of recent users and in correct order."""

        monkeypatch.setattr("forum.cache.repository.LAST_N", 3)
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username2"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username3"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username4"
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await test_redis.lrange(RECENT_USERS_KEY, 0, -1)

        assert len(recent_users) == 3

        data = UserRead.model_validate_json(recent_users[0])
        assert data.username == "username4"
        data = UserRead.model_validate_json(recent_users[1])
        assert data.username == "username3"
        data = UserRead.model_validate_json(recent_users[2])
        assert data.username == "username2"


class TestCacheGetRecentUsers:
    async def test_get_with_empty_users(self, cache_repo: CacheRepository, test_redis):
        """Empty list should be returned."""
        users = await cache_repo.get_recent_users(test_redis)

        assert users == []

    async def test_with_one_user(
        self, cache_repo: CacheRepository, test_redis, test_readuser
    ):
        """Return the only user."""
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await cache_repo.get_recent_users(test_redis)
        assert len(recent_users) == 1
        assert recent_users[0].username == VALID_USERNAME

    async def test_get_exactly_max_recent_users(
        self, cache_repo: CacheRepository, test_redis, test_readuser, monkeypatch
    ):
        """Return the exactly max number of recent users."""
        monkeypatch.setattr("forum.cache.repository.LAST_N", 3)
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username2"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username3"
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await cache_repo.get_recent_users(test_redis)

        assert len(recent_users) == 3
        assert recent_users[0].username == "username3"
        assert recent_users[1].username == "username2"
        assert recent_users[2].username == VALID_USERNAME

    async def test_get_one_more_than_max_recent_users(
        self, cache_repo: CacheRepository, test_redis, test_readuser, monkeypatch
    ):
        """Return the exactly max number of recent users when it was added more than the max."""
        monkeypatch.setattr("forum.cache.repository.LAST_N", 2)
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username2"
        await cache_repo.push_recent_user(test_redis, test_readuser)
        test_readuser.username = "username3"
        await cache_repo.push_recent_user(test_redis, test_readuser)

        recent_users = await cache_repo.get_recent_users(test_redis)

        assert len(recent_users) == 2
        assert recent_users[0].username == "username3"
        assert recent_users[1].username == "username2"
