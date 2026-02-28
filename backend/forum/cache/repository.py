import logging

from redis.asyncio import Redis

from forum.auth.schemas import UserRead

log = logging.getLogger(__name__)

RECENT_USERS_KEY = "recent_users"
LAST_N = 10
USER_POSTS_KEY = "user_posts"
FORUM_POSTS_KEY = "forum_posts"
FORUM_THREADS_KEY = "forum_threads"


class CacheRepository:
    """Manage caching"""

    async def push_recent_user(self, cache: Redis, user: UserRead):
        """Push user to cache to keep track of the recent users."""
        user_data = UserRead.model_validate(user)
        try:
            async with cache.pipeline(transaction=True) as pipe:
                await pipe.lpush(RECENT_USERS_KEY, user_data.model_dump_json())  # type: ignore
                await pipe.ltrim(RECENT_USERS_KEY, 0, LAST_N - 1)  # type: ignore
                await pipe.execute()
            log.info(f"Cached {user}")
        except Exception as e:
            log.error(f"Error during caching new user: {user}: {e}")

    async def get_recent_users(self, cache: Redis) -> list[UserRead]:
        """Retrieve the recent 10 registered users."""
        users = await cache.lrange(RECENT_USERS_KEY, 0, LAST_N - 1)  # type: ignore
        return [UserRead.model_validate_json(user) for user in users]

    async def on_post_created(self, cache: Redis, user_id: int, forum_id: int):
        """
        Update cache after a post is created.
        Increments user total posts and a forum total posts.
        """
        async with cache.pipeline() as pipe:
            await pipe.incr(f"{USER_POSTS_KEY}:{user_id}")
            await pipe.incr(f"{FORUM_POSTS_KEY}:{forum_id}")
            await pipe.execute()

    async def on_post_deleted(self, cache: Redis, user_id: int, forum_id: int):
        """
        Update cache after a post is deleted.
        Decrements user total posts and a forum total posts.
        """
        async with cache.pipeline() as pipe:
            await pipe.decr(f"{USER_POSTS_KEY}:{user_id}")
            await pipe.decr(f"{FORUM_POSTS_KEY}:{forum_id}")
            await pipe.execute()

    async def on_thread_created(self, cache: Redis, forum_id: int):
        """
        Update cache after a thread is created.
        Incremets forum total threads.
        """
        await cache.incr(f"{FORUM_THREADS_KEY}:{forum_id}")

    async def on_thread_deleted(self, cache: Redis, forum_id: int):
        """
        Update cache after a thread is deleted.
        Deletes forum total threads.
        """
        await cache.decr(f"{FORUM_THREADS_KEY}:{forum_id}")

    async def on_forum_read(self, cache: Redis, forum_id: int) -> tuple[int, int]:
        """
        Read cache for forum.
        Returns the total posts of a forum and the number of threads.
        """
        async with cache.pipeline(transaction=False) as pipe:
            await pipe.get(f"{FORUM_POSTS_KEY}:{forum_id}")
            await pipe.get(f"{FORUM_THREADS_KEY}:{forum_id}")
            res = await pipe.execute()
        return (res[0] or 0, res[1] or 0)

    async def get_user_total_posts(self, cache: Redis, user_id: int) -> int | None:
        """Get the total number of posts of a user."""
        return await cache.get(f"{USER_POSTS_KEY}:{user_id}")


cache_repo = CacheRepository()
