from fastapi import APIRouter
from forum.auth.router import auth_router, user_router
from forum.category.router import category_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(category_router)
