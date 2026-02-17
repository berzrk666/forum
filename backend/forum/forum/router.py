import logging
from fastapi import APIRouter, Depends, HTTPException, status

from forum.auth.dependencies import get_admin_user
from forum.database.core import DbSession
from forum.forum.exceptions import CategoryDoesNotExist, ForumDoesNotExist
from forum.forum.schemas import ForumCreate, ForumEdit, ForumPagination, ForumRead
from forum.forum.service import forum_service as srvc

log = logging.getLogger(__name__)

forum_router = APIRouter(prefix="/forums", tags=["forums"])


@forum_router.post(
    "/",
    response_model=ForumRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_user)],
)
async def create_forum(db_session: DbSession, forum_in: ForumCreate):
    """Create a forum."""
    try:
        forum = await srvc.create(db_session, forum_in)
        return forum
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@forum_router.get("/", response_model=ForumPagination)
async def list_all_forums(db_session: DbSession):
    """List all forums."""
    try:
        forums = await srvc.list(db_session)
        forums_data = [ForumRead.model_validate(f) for f in forums]
        return ForumPagination(data=forums_data)
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@forum_router.put(
    "/{id}", response_model=ForumRead, dependencies=[Depends(get_admin_user)]
)
async def update_forum(db_session: DbSession, id: int, forum_in: ForumEdit):
    """Update a forum."""
    try:
        forum = await srvc.update(db_session, id, forum_in)
        return forum
    except ForumDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Forum does not exist")
    except CategoryDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category does not exist")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
