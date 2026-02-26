import logging

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from forum.auth.models import User
from forum.forum.exceptions import ForumDoesNotExist
from forum.forum.models import Forum
from forum.thread.exception import ThreadDoesNotExist, ThreadNotOwner
from forum.thread.models import Thread
from forum.thread.schemas import ThreadCreate, ThreadEditUser

log = logging.getLogger(__name__)


class ThreadService:
    async def create(
        self, session: AsyncSession, thread_in: ThreadCreate, author: User
    ):
        """Create a new Thread."""
        forum = await session.get(Forum, thread_in.forum_id)
        if forum is None:
            raise ForumDoesNotExist

        try:
            thread = Thread(**thread_in.model_dump())
            thread.forum = forum
            thread.author = author
            session.add(thread)
            await session.flush()
            await session.refresh(thread)
            return thread
        except Exception as e:
            log.error(f"Unexpected error when creating a new Thread {thread_in}: {e}")
            raise

    async def list_threads(
        self, session: AsyncSession, forum_id: int, page: int, limit: int
    ) -> tuple[list[Thread], int]:
        """
        List threads paginated under a forum.
        Returns list of threads and number of total threads.
        """
        forum = await session.get(Forum, forum_id)
        if forum is None:
            raise ForumDoesNotExist

        try:
            count_st = (
                select(func.count())
                .select_from(Thread)
                .where(Thread.forum_id == forum_id)
            )
            st = (
                select(Thread)
                .where(Thread.forum_id == forum_id)
                .options(selectinload(Thread.author))
                .order_by(Thread.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )

            threads = await session.scalars(st)
            total = await session.scalar(count_st) or 0
            return threads.all(), total  # type: ignore
        except Exception as e:
            log.error(
                f"Unexpected error when listing threads under Forum:{forum_id}: {e}"
            )
            raise

    async def get(self, session: AsyncSession, id: int) -> Thread:
        """Get a thread by ID."""
        thread = await session.get(
            Thread,
            id,
            options=[selectinload(Thread.author), selectinload(Thread.forum)],
        )
        if thread is None:
            raise ThreadDoesNotExist
        return thread

    async def pin(self, session: AsyncSession, id: int) -> Thread:
        """Pin a thread by ID."""
        thread = await session.get(Thread, id, options=[selectinload(Thread.author)])
        if thread is None:
            raise ThreadDoesNotExist
        thread.is_pinned = True
        return thread

    async def unpin(self, session: AsyncSession, id: int) -> Thread:
        """Unpin a thread by ID."""
        thread = await session.get(Thread, id, options=[selectinload(Thread.author)])
        if thread is None:
            raise ThreadDoesNotExist
        thread.is_pinned = False
        return thread

    async def lock(self, session: AsyncSession, id: int) -> Thread:
        """Lock a thread by ID."""
        thread = await session.get(Thread, id, options=[selectinload(Thread.author)])
        if thread is None:
            raise ThreadDoesNotExist
        thread.is_locked = True
        return thread

    async def unlock(self, session: AsyncSession, id: int) -> Thread:
        """Unlock a thread by ID."""
        thread = await session.get(Thread, id, options=[selectinload(Thread.author)])
        if thread is None:
            raise ThreadDoesNotExist
        thread.is_locked = False
        return thread

    async def edit(
        self, session: AsyncSession, id: int, thread_in: ThreadEditUser, user: User
    ) -> Thread:
        """Edit a thread."""
        thread = await self.get(session, id)
        if thread.author != user and not user.is_moderator():
            raise ThreadNotOwner
        try:
            data = thread_in.model_dump()
            for field, value in data.items():
                if value is not None:
                    setattr(thread, field, value)

            await session.flush()
            await session.refresh(thread)
            return thread
        except Exception as e:
            log.error(f"Error while trying to edit the Thread {id}: {e}")
            raise


thread_service = ThreadService()
