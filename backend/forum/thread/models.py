from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Text
from forum.database.core import Base, TimestampMixin

if TYPE_CHECKING:
    from forum.auth.models import User
    from forum.forum.models import Forum
    from forum.post.models import Post


class Thread(Base, TimestampMixin):
    """SQLAlchemy model for a Thread."""

    __tablename__ = "threads"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(default=False)
    is_locked: Mapped[bool] = mapped_column(default=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="threads")

    forum_id: Mapped[int] = mapped_column(ForeignKey("forums.id"))
    forum: Mapped["Forum"] = relationship(back_populates="threads")

    posts: Mapped[list["Post"]] = relationship(back_populates="thread")
