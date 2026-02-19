from fastapi import APIRouter

from forum.auth.router import auth_router, user_router
from forum.category.router import category_router
from forum.forum.router import forum_router
from forum.thread.router import thread_router
from forum.post.router import post_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(category_router)
api_router.include_router(forum_router)
api_router.include_router(thread_router)
api_router.include_router(post_router)
