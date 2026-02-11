from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from forum.config import settings

Base = declarative_base()

engine = create_async_engine(str(settings.DATABASE_URI))
sessionlocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with auto-commit."""
    async with sessionlocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class TimestampMixin:
    """Timestamp Mixin for created_at and updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(True), server_default=func.now(), onupdate=func.now()
    )
