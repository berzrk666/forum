import logging

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from forum.category.models import Category
from forum.forum.exceptions import CategoryDoesNotExist, ForumDoesNotExist
from forum.forum.models import Forum
from forum.forum.schemas import ForumCreate, ForumEdit, ForumRead
from forum.cache.repository import cache_repo

log = logging.getLogger(__name__)


class ForumService:
    async def create(self, session: AsyncSession, forum_in: ForumCreate) -> Forum:
        """Create a new Forum."""
        category = await session.get(Category, forum_in.category_id)
        if not category:
            raise CategoryDoesNotExist

        try:
            if forum_in.order is None:
                max_order = await session.scalar(func.max(Forum.order))
                forum_in.order = (max_order or 0) + 1

            forum = Forum(**forum_in.model_dump())
            session.add(forum)
            await session.flush()
            await session.refresh(forum)

            # Load Category data
            # PERF: You don't need this query if you the same with
            # the update() method: forum.category = category
            await session.get(
                Forum,
                forum.id,
                populate_existing=True,
                options=[selectinload(Forum.category)],
            )
            return forum
        except IntegrityError as e:
            # TODO: Raises error if category_id does not exist
            log.error(e.orig)
            log.warning("IntegrityError")
            raise
        except Exception as e:
            log.error(f"Unexpected error when creating a new forum {forum_in}: {e}")
            raise

    async def list(self, session: AsyncSession) -> list[Forum]:
        """List all forums."""
        try:
            st = (
                select(Forum)
                .options(selectinload(Forum.category))
                .order_by(Forum.order)
            )
            forums = await session.scalars(st)
            return forums.all()  # type: ignore
        except Exception as e:
            log.error(f"Unexpected error when listing all forums: {e}")
            raise

    async def update(
        self, session: AsyncSession, id: int, forum_in: ForumEdit
    ) -> ForumRead:
        """Update forum."""
        forum = await session.get(Forum, id)
        if forum is None:
            raise ForumDoesNotExist

        category = await session.get(Category, forum_in.category_id)
        if category is None:
            raise CategoryDoesNotExist

        try:
            if forum_in.name:
                forum.name = forum_in.name

            if forum_in.category_id:
                forum.category = category

            if forum_in.description:
                forum.description = forum_in.description

            if forum_in.order:
                forum.order = forum_in.order

            session.add(forum)
            await session.flush()
            await session.refresh(forum)
            # For some reason this is needed here
            forum.category = category
            return forum
        except Exception as e:
            log.error(f"Unexpected error when updating forum {id}: {e}")
            raise


forum_service = ForumService()
