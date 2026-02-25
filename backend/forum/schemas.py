from pydantic import BaseModel, ConfigDict


class Pagination(BaseModel):
    """Pydantic model for pagination"""

    page: int
    page_size: int
    total_items: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
