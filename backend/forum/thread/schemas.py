from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.types import PositiveInt


class Author(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class ThreadBase(BaseModel):
    title: str

    model_config = ConfigDict(from_attributes=True)


class ThreadCreate(ThreadBase):
    forum_id: PositiveInt


class ThreadRead(ThreadBase):
    author: Author
    created_at: datetime
    is_pinned: bool
    is_locked: bool


class ThreadPagination(BaseModel):
    data: list[ThreadRead]
