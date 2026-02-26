from pydantic import BaseModel

from forum.auth.schemas import UserRead


class DashboardStats(BaseModel):
    """Pydantic schema for dashboard stats."""

    n_users: int
    n_categories: int
    n_forums: int
    n_threads: int
    n_posts: int
    recent_users: list[UserRead]
