import logging

from fastapi import APIRouter, HTTPException, status

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
async def list_thread_posts(db_session: DbSession, id: int):
    """List all posts in a thread."""
    try:
        posts = await srvc.list_posts(db_session, id)
        posts_data = [PostRead.model_validate(p) for p in posts]
        return PostPagination(data=posts_data)
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
