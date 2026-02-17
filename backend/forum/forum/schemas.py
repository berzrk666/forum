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
    order: PositiveInt
    category: CategoryRead


class ForumPagination(BaseModel):
    data: list[ForumRead]
