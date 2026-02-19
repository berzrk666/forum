import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from forum.auth.models import User
from forum.post.exceptions import ThreadIsLocked
from forum.post.models import Post
from forum.post.schemas import PostCreate
from forum.thread.exception import ThreadDoesNotExist
from forum.thread.models import Thread

log = logging.getLogger(__name__)


class PostService:
    async def create(
        self, session: AsyncSession, post_in: PostCreate, author: User
    ) -> Post:
        """Create a post."""
        try:
            thread = await session.get(Thread, post_in.thread_id)
            if thread is None:
                raise ThreadDoesNotExist

            if thread.is_locked:
                raise ThreadIsLocked

            post = Post(**post_in.model_dump())
            post.thread = thread
            post.author = author

            session.add(post)
            await session.flush()
            await session.refresh(post)
            return post
        except Exception as e:
            log.error(f"Unexpected error when creating a new Post {post_in}: {e}")
            raise

    async def list_posts(self, session: AsyncSession, id: int) -> list[Post]:
        """List all posts from a thread."""
        try:
            thread = await session.get(Thread, id)
            if thread is None:
                raise ThreadDoesNotExist

            st = (
                select(Post)
                .where(Post.thread_id == id)
                .order_by(Post.created_at)
                .options(selectinload(Post.author))
            )
            posts = await session.scalars(st)
            return posts  # type: ignore
        except Exception as e:
            log.error(f"Unexpected error when listing all posts for Thread {id}: {e}")
            raise


post_service = PostService()
