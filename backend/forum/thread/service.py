import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from forum.auth.models import User
from forum.forum.exceptions import ForumDoesNotExist
from forum.forum.models import Forum
from forum.thread.exception import ThreadDoesNotExist
from forum.thread.models import Thread
from forum.thread.schemas import ThreadCreate

log = logging.getLogger(__name__)


class ThreadService:
    async def create(
        self, session: AsyncSession, thread_in: ThreadCreate, author: User
    ):
        """Create a new Thread."""
        try:
            forum = await session.get(Forum, thread_in.forum_id)
            if forum is None:
                raise ForumDoesNotExist
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

    async def list_threads(self, session: AsyncSession, forum_id: int) -> list[Thread]:
        """List all threads under a forum."""
        try:
            forum = await session.get(Forum, forum_id)
            if forum is None:
                raise ForumDoesNotExist

            st = (
                select(Thread)
                .where(Thread.forum_id == forum_id)
                .options(selectinload(Thread.author))
                .order_by(Thread.created_at.desc())
            )
            threads = await session.scalars(st)
            return threads.all()  # type: ignore
        except Exception as e:
            log.error(
                f"Unexpected error when listing threads under Forum:{forum_id}: {e}"
            )
            raise

    async def get(self, session: AsyncSession, id: int) -> Thread:
        """Get a thread by ID."""
        try:
            thread = await session.get(
                Thread,
                id,
                options=[selectinload(Thread.author), selectinload(Thread.forum)],
            )
            if thread is None:
                raise ThreadDoesNotExist

            return thread
        except Exception as e:
            log.error(f"Unexpected error when retrieve thread:{id}: {e}")
            raise

    async def pin(self, session: AsyncSession, id: int) -> Thread:
        """Pin a thread by ID."""
        try:
            thread = await session.get(
                Thread, id, options=[selectinload(Thread.author)]
            )
            if thread is None:
                raise ThreadDoesNotExist
            thread.is_pinned = True
            return thread
        except Exception as e:
            log.error(f"Unexpected error when pinning thread:{id}: {e}")
            raise

    async def unpin(self, session: AsyncSession, id: int) -> Thread:
        """Unpin a thread by ID."""
        try:
            thread = await session.get(
                Thread, id, options=[selectinload(Thread.author)]
            )
            if thread is None:
                raise ThreadDoesNotExist
            thread.is_pinned = False
            return thread
        except Exception as e:
            log.error(f"Unexpected error when unpinning thread:{id}: {e}")
            raise

    async def lock(self, session: AsyncSession, id: int) -> Thread:
        """Lock a thread by ID."""
        try:
            thread = await session.get(
                Thread, id, options=[selectinload(Thread.author)]
            )
            if thread is None:
                raise ThreadDoesNotExist
            thread.is_locked = True
            return thread
        except Exception as e:
            log.error(f"Unexpected error when locking thread:{id}: {e}")
            raise

    async def unlock(self, session: AsyncSession, id: int) -> Thread:
        """Unlock a thread by ID."""
        try:
            thread = await session.get(
                Thread, id, options=[selectinload(Thread.author)]
            )
            if thread is None:
                raise ThreadDoesNotExist
            thread.is_locked = False
            return thread
        except Exception as e:
            log.error(f"Unexpected error when unlocking thread:{id}: {e}")
            raise


thread_service = ThreadService()
