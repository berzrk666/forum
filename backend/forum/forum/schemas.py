from pydantic import BaseModel, ConfigDict

from forum.category.schemas import CategoryRead


class ForumBase(BaseModel):
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ForumCreate(ForumBase):
    category_id: int


class ForumRead(ForumBase):
    category: CategoryRead


class ForumPagination(BaseModel):
    data: list[ForumRead]
