import logging

from sqlalchemy.ext.asyncio import AsyncSession

from forum.forum.models import Forum
from forum.forum.schemas import ForumCreate

log = logging.getLogger(__name__)


class ForumService:
    async def create(self, session: AsyncSession, forum_in: ForumCreate) -> Forum:
        """Create a new Forum."""
        try:
            forum = Forum(**forum_in.model_dump())
            pass
        except Exception as e:
            log.error(f"Unexpected error when creating a new forum {forum_in}: {e}")
            raise
