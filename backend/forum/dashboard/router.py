import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status

from forum.auth.dependencies import get_moderator_user
from forum.dashboard.schemas import DashboardStats
from forum.database.core import DbSession
from forum.dashboard.service import dash_service as srvc


dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

log = logging.getLogger(__name__)


@dashboard_router.get(
    "/", response_model=DashboardStats, dependencies=[Depends(get_moderator_user)]
)
async def get_stats(db_session: DbSession, request: Request):
    try:
        return await srvc.get_stats(db_session, request.app.state.cache)
    except Exception:
        log.error("failed to get stats", exc_info=True)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
