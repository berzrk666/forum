import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from forum.category.exceptions import CategoryAlreadyExists
from forum.category.models import Category
from forum.category.schemas import CategoryCreate

log = logging.getLogger(__name__)


class CategoryService:
    async def create(self, session: AsyncSession, data_in: CategoryCreate) -> Category:
        """Create a new Category."""
        try:
            if data_in.order is None:
                max_order = await session.scalar(func.max(Category.order))
                data_in.order = (max_order or 0) + 1
            category = Category(**data_in.model_dump())
            session.add(category)
            await session.flush()
            await session.refresh(category)
            return category
        except IntegrityError:
            # TODO: Check if its the category name is in conflict or the order
            raise CategoryAlreadyExists
        except Exception as e:
            log.error(f"Unexpected error when creating a new category {data_in}: {e}")
            raise

    async def list(self, session: AsyncSession) -> list[Category]:
        """List all categories ordered by their order."""
        try:
            st = select(Category).order_by(Category.order)
            res = await session.scalars(st)
            return res.all()  # type: ignore
        except Exception as e:
            log.error(f"Unexpected error when listing categories: {e}")
            raise


category_service = CategoryService()
