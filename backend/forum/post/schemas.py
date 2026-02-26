from datetime import datetime
from pydantic import BaseModel, ConfigDict

from forum.schemas import Pagination
from forum.thread.schemas import Author


class PostBase(BaseModel):
    thread_id: int
    content: str

    model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    id: int
    author: Author
    created_at: datetime
    updated_at: datetime


class PostEditUser(BaseModel):
    content: str

    model_config = ConfigDict(from_attributes=True)


class PostPagination(Pagination):
    data: list[PostRead]
