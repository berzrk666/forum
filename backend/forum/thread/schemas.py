from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.types import PositiveInt

from forum.schemas import Pagination


class Author(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class ThreadBase(BaseModel):
    title: str

    model_config = ConfigDict(from_attributes=True)


class ThreadCreate(ThreadBase):
    forum_id: PositiveInt
    content: str


class ThreadRead(ThreadBase):
    id: int
    author: Author
    content: str
    created_at: datetime
    is_pinned: bool
    is_locked: bool


class ThreadEditUser(BaseModel):
    """Pydantic schema when a user update their own thread."""

    title: str | None = None
    content: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ThreadPagination(Pagination):
    data: list[ThreadRead]
