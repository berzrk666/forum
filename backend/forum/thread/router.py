from fastapi import APIRouter, HTTPException, status

from forum.auth.dependencies import CurrentUser
from forum.database.core import DbSession
from forum.thread.schemas import ThreadCreate, ThreadPagination, ThreadRead
from forum.thread.service import thread_service as srvc
from forum.forum.router import forum_router


thread_router = APIRouter(prefix="/thread", tags=["threads"])


@thread_router.post("/", response_model=ThreadRead)
async def create_thread(
    db_session: DbSession, thread_in: ThreadCreate, current_user: CurrentUser
):
    """Create a thread."""
    try:
        thread = await srvc.create(db_session, thread_in, current_user)
        return thread
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@forum_router.get("/{id}/threads", response_model=ThreadPagination)
async def list_threads_under_forum(db_session: DbSession, id: int):
    """Create a thread."""
    try:
        threads = await srvc.list_threads(db_session, id)
        threads_data = [ThreadRead.model_validate(t) for t in threads]
        return ThreadPagination(data=threads_data)
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
