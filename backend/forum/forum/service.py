import logging
from types import NoneType

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from forum.category.models import Category
from forum.forum.exceptions import CategoryDoesNotExist
from forum.forum.models import Forum
from forum.forum.schemas import ForumCreate

log = logging.getLogger(__name__)


class ForumService:
    async def create(self, session: AsyncSession, forum_in: ForumCreate) -> Forum:
        """Create a new Forum."""
        try:
            category = await session.get(Category, forum_in.category_id)
            if not category:
                raise CategoryDoesNotExist

            if forum_in.order is None:
                max_order = await session.scalar(func.max(Forum.order))
                forum_in.order = (max_order or 0) + 1

            forum = Forum(**forum_in.model_dump())
            session.add(forum)
            await session.commit()
            await session.refresh(forum)

            # Load Category data
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


forum_service = ForumService()
