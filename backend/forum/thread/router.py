import math
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import PositiveInt

from forum.auth.dependencies import CurrentUser, get_moderator_user
from forum.database.core import DbSession
from forum.thread.exception import ThreadDoesNotExist, ThreadNotOwner
from forum.thread.schemas import (
    ThreadCreate,
    ThreadEditUser,
    ThreadPagination,
    ThreadRead,
)
from forum.thread.service import thread_service as srvc
from forum.forum.router import forum_router


thread_router = APIRouter(prefix="/thread", tags=["threads"])


@thread_router.post("/", response_model=ThreadRead)
async def create_thread(
    db_session: DbSession,
    request: Request,
    thread_in: ThreadCreate,
    current_user: CurrentUser,
):
    """Create a thread."""
    try:
        thread = await srvc.create(
            db_session, request.app.state.cache, thread_in, current_user
        )
        return thread
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@forum_router.get("/{id}/threads", response_model=ThreadPagination)
async def list_threads_under_forum(
    db_session: DbSession, id: int, page: PositiveInt = 1, limit: PositiveInt = 15
):
    """List threads paginated under a forum."""
    try:
        threads, total_items = await srvc.list_threads(db_session, id, page, limit)
        threads_data = [ThreadRead.model_validate(t) for t in threads]
        page_size = len(threads)
        return ThreadPagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=math.ceil(total_items / limit) if total_items else 0,
            data=threads_data,
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.get("/{id}", response_model=ThreadRead)
async def read_thread(db_session: DbSession, id: int):
    """Read a thread."""
    try:
        thread = await srvc.get(db_session, id)
        return thread
    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.patch(
    "/{id}/pin",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_moderator_user)],
    response_model=ThreadRead,
)
async def pin_thread(db_session: DbSession, id: int):
    """Pin a thread."""
    try:
        return await srvc.pin(db_session, id)
    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.patch(
    "/{id}/unpin",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_moderator_user)],
    response_model=ThreadRead,
)
async def unpin_thread(db_session: DbSession, id: int):
    """Unpin a thread."""
    try:
        return await srvc.unpin(db_session, id)
    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.patch(
    "/{id}/lock",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_moderator_user)],
    response_model=ThreadRead,
)
async def lock_thread(db_session: DbSession, id: int):
    """Lock a thread."""
    try:
        return await srvc.lock(db_session, id)
    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.patch(
    "/{id}/unlock",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_moderator_user)],
    response_model=ThreadRead,
)
async def unlock_thread(db_session: DbSession, id: int):
    """Unlock a thread."""
    try:
        return await srvc.unlock(db_session, id)
    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@thread_router.patch(
    "/{id}/edit",
    status_code=status.HTTP_200_OK,
    response_model=ThreadRead,
)
async def edit_thread(
    db_session: DbSession, id: int, thread_in: ThreadEditUser, current_user: CurrentUser
):
    """Edit an existing thread."""
    try:
        return await srvc.edit(db_session, id, thread_in, current_user)
    except ThreadDoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thread does not exist.")
    except ThreadNotOwner:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "You can not edit a thread you did not create.",
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
