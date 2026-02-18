from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from forum.auth.models import User
from forum.database.core import Base, TimestampMixin
from forum.forum.models import Forum


class Thread(Base, TimestampMixin):
    """SQLAlchemy model for a Thread."""

    __tablename__ = "threads"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_pinned: Mapped[bool] = mapped_column(default=False)
    is_locked: Mapped[bool] = mapped_column(default=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship(back_populates="threads")

    forum_id: Mapped[int] = mapped_column(ForeignKey("forums.id"))
    forum: Mapped[Forum] = relationship(back_populates="threads")
