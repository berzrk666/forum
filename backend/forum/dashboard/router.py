from fastapi import APIRouter, Depends, Request

from forum.auth.dependencies import get_moderator_user
from forum.dashboard.schemas import DashboardStats
from forum.database.core import DbSession
from forum.dashboard.service import dash_service as srvc


dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get(
    "/", response_model=DashboardStats, dependencies=[Depends(get_moderator_user)]
)
async def get_stats(db_session: DbSession, request: Request):
    return await srvc.get_stats(db_session, request.app.state.cache)
