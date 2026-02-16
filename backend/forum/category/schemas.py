from pydantic import BaseModel, ConfigDict
from pydantic.types import PositiveInt


class CategoryBase(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(CategoryBase):
    order: PositiveInt | None = None


class CategoryRead(CategoryBase):
    id: int
    order: PositiveInt


class CategoryPagination(BaseModel):
    data: list[CategoryRead]
