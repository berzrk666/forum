from pydantic import BaseModel, ConfigDict
from pydantic.types import PositiveInt

from forum.category.schemas import CategoryRead


class ForumBase(BaseModel):
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ForumCreate(ForumBase):
    category_id: int
    order: PositiveInt | None = None


class ForumRead(ForumBase):
    id: int
    order: PositiveInt
    category: CategoryRead
    n_posts: int = 0
    n_threads: int = 0


class ForumEdit(BaseModel):
    """Pydantic schema to update a forum."""

    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    order: PositiveInt | None = None


class ForumPagination(BaseModel):
    data: list[ForumRead]
