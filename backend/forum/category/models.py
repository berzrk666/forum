from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer
from forum.database.core import Base
from forum.forum.models import Forum


class Category(Base):
    """SQLAlchemy model for a Category."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    forums: Mapped[list[Forum]] = relationship(back_populates="category")
