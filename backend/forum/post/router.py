import logging
import math

from fastapi import APIRouter, HTTPException, status
from pydantic.types import PositiveInt

from forum.auth.dependencies import CurrentUser
from forum.database.core import DbSession
from forum.post.exceptions import ThreadIsLocked
from forum.post.schemas import PostCreate, PostPagination, PostRead
from forum.post.service import post_service as srvc
from forum.thread.exception import ThreadDoesNotExist
from forum.thread.router import thread_router

log = logging.getLogger(__name__)

post_router = APIRouter(prefix="/posts", tags=["posts"])


@post_router.post("/", response_model=PostRead)
async def create_post(
    db_session: DbSession, current_user: CurrentUser, post_in: PostCreate
):
    """Create a post under a thread"""
    try:
        post = await srvc.create(db_session, post_in, current_user)
        return post

    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist")

    except ThreadIsLocked:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "You cannot post in a thread that is locked"
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.get("/{id}/posts", response_model=PostPagination)
async def list_thread_posts(
    db_session: DbSession, id: int, page: PositiveInt = 1, limit: PositiveInt = 10
):
    """List all posts in a thread."""
    try:
        posts, total_items = await srvc.list_posts(db_session, id, page, limit)
        posts_data = [PostRead.model_validate(p) for p in posts]
        page_size = len(posts)
        return PostPagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=math.ceil(total_items / limit) if total_items > 0 else 0,
            data=posts_data,
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
