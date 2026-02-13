from typing import Annotated, AsyncGenerator

from fastapi import Depends
import redis.asyncio as redis

from forum.config import settings


async def get_cache() -> AsyncGenerator[redis.Redis, None]:
    client = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    try:
        yield client
    except Exception:
        await client.aclose()
        raise


CacheClient = Annotated[redis.Redis, Depends(get_cache)]
