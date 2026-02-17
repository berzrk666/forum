from pydantic import BaseModel, ConfigDict
from pydantic.types import PositiveInt

from forum.category.schemas import CategoryRead


class ForumBase(BaseModel):
    name: str
    description: str
    order: PositiveInt

    model_config = ConfigDict(from_attributes=True)


class ForumCreate(ForumBase):
    category_id: int


class ForumRead(ForumBase):
    category: CategoryRead


class ForumPagination(BaseModel):
    data: list[ForumRead]
