from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from forum.database.core import Base

if TYPE_CHECKING:
    from forum.category.models import Category
else:
    Category = "Category"


class Forum(Base):
    """SQLAlchemy model for a Forum."""

    __tablename__ = "forums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="forums")
