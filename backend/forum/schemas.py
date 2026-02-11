from pydantic import BaseModel, ConfigDict


class Pagination(BaseModel):
    """Pydantic model for pagination"""

    itemPerPage: int
    page: int
    total: int

    model_config = ConfigDict(from_attributes=True)
