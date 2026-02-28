import logging

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from forum.auth.models import User
from forum.cache.repository import cache_repo
from forum.category.models import Category
from forum.dashboard.schemas import DashboardStats
from forum.forum.models import Forum
from forum.post.models import Post
from forum.thread.models import Thread

log = logging.getLogger(__name__)


class DashboardService:
    async def get_stats(self, session: AsyncSession, cache: Redis) -> DashboardStats:
        """Get dashboard stats."""
        stmt = select(
            select(func.count()).select_from(User).scalar_subquery(),
            select(func.count()).select_from(Category).scalar_subquery(),
            select(func.count()).select_from(Forum).scalar_subquery(),
            select(func.count()).select_from(Thread).scalar_subquery(),
            select(func.count()).select_from(Post).scalar_subquery(),
        )
        res = (await session.execute(stmt)).one()
        users = await cache_repo.get_recent_users(cache)

        return DashboardStats(
            n_users=res[0],
            n_categories=res[1],
            n_forums=res[2],
            n_threads=res[3],
            n_posts=res[4],
            recent_users=users,
        )


dash_service = DashboardService()
