import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from forum.auth.models import User
from forum.post.exceptions import ThreadIsLocked
from forum.post.models import Post
from forum.post.schemas import PostCreate, PostPagination
from forum.thread.exception import ThreadDoesNotExist
from forum.thread.models import Thread

log = logging.getLogger(__name__)


class PostService:
    async def create(
        self, session: AsyncSession, post_in: PostCreate, author: User
    ) -> Post:
        """Create a post."""
        thread = await session.get(Thread, post_in.thread_id)
        if thread is None:
            raise ThreadDoesNotExist
        if thread.is_locked:
            raise ThreadIsLocked

        try:
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

    async def list_posts(
        self, session: AsyncSession, id: int, page: int, limit: int
    ) -> tuple[list[Post], int]:
        """
        List posts paginated from a thread.
        Returns a list of posts and the total number of posts.
        """
        thread = await session.get(Thread, id)
        if thread is None:
            raise ThreadDoesNotExist
        try:
            count_st = (
                select(func.count()).select_from(Post).where(Post.thread_id == id)
            )
            st = (
                select(Post)
                .where(Post.thread_id == id)
                .order_by(Post.created_at)
                .options(selectinload(Post.author))
                .offset((page - 1) * limit)
                .limit(limit)
            )
            posts = (await session.scalars(st)).all()
            total = await session.scalar(count_st) or 0

            return posts, total  # type: ignore
        except Exception as e:
            log.error(f"Unexpected error when listing all posts for Thread {id}: {e}")
            raise


post_service = PostService()
