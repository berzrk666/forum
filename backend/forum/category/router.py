import logging

from fastapi import APIRouter, HTTPException, status

from forum.category.exceptions import CategoryAlreadyExists
from forum.category.schemas import CategoryCreate, CategoryPagination, CategoryRead
from forum.database.core import DbSession
from forum.category.service import category_service as cat_srvc

log = logging.getLogger(__name__)

category_router = APIRouter(prefix="/category", tags=["category"])


@category_router.post(
    "/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED
)
async def create_category(db_session: DbSession, category_in: CategoryCreate):
    """Create a Category."""
    try:
        cat = await cat_srvc.create(db_session, category_in)
        return cat

    except CategoryAlreadyExists:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name or order already exists."
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@category_router.get("/", response_model=CategoryPagination)
async def get_categories(db_session: DbSession):
    """Get list of categories."""
    try:
        cats = await cat_srvc.list(db_session)
        return cats
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )
