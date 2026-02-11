from fastapi import APIRouter
from forum.auth.schemas import UserLogin


auth_router = APIRouter(prefix="/auth", tags=["authorization"])


@auth_router.post("/login")
async def login_endpoint(user_in: UserLogin):
    """Login."""
    return user_in
