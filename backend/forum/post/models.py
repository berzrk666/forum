from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text
from forum.database.core import Base, TimestampMixin

if TYPE_CHECKING:
    from forum.thread.models import Thread
    from forum.auth.models import User


class Post(Base, TimestampMixin):
    """SQLAlchemy model for a Post."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    thread: Mapped["Thread"] = relationship(back_populates="posts")
