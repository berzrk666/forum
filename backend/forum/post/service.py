import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from forum.auth.models import User
from forum.post.exceptions import PostDoesNotExist, PostNotOwner, ThreadIsLocked
from forum.post.models import Post
from forum.post.schemas import PostCreate, PostEditUser
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

    async def get(self, session: AsyncSession, id: int) -> Post:
        """Retrieve a post from database. Raises PostDoesNotExist."""
        post = await session.get(
            Post, id, options=[selectinload(Post.author), selectinload(Post.thread)]
        )
        if post is None:
            raise PostDoesNotExist
        return post

    async def edit(
        self, session: AsyncSession, id: int, user: User, post_in: PostEditUser
    ) -> Post:
        """
        Update a post. Only allows for editing owned posts or if user
        is a moderator or admin.

        Returns the updated post.
        """
        post = await self.get(session, id)

        if post.author != user and not user.is_moderator():
            raise PostNotOwner

        log.debug(f"Post {id} modified by {user}")
        data = post_in.model_dump()
        for field, value in data.items():
            if value is not None:
                setattr(post, field, value)
        await session.flush()
        await session.refresh(post)
        return post


post_service = PostService()
