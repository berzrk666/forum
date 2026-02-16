import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from forum.auth.dependencies import (
    CurrentUser,
    get_moderator_user,
)
from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    UsernameAlreadyExists,
)
from forum.auth.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserPagination,
    UserRead,
)
from forum.auth.service import auth as auth_service
from forum.database.core import DbSession

auth_router = APIRouter(prefix="/auth", tags=["authorization"])
user_router = APIRouter(prefix="/users", tags=["users"])

log = logging.getLogger(__name__)


@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_endpoint(
    db_session: DbSession,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
):
    """Login endpoint."""
    try:
        user_in = UserLogin(username=user_data.username, password=user_data.password)
        user = await auth_service.authenticate(db_session, request, user_in)
        # token = Token(access_token=user.token)
        # return UserLoginResponse(token=token)
        await request.app.state.cache.sadd("users", user.username)
        await request.app.state.cache.sadd(f"users_perms:{user.id}", "posts:read")
        await request.app.state.cache.sadd(f"users_perms:{user.id}", "posts:edit")
        return Token(access_token=user.token)
    except IncorrectPasswordOrUsername:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@auth_router.post(
    "/register", response_model=Token, status_code=status.HTTP_201_CREATED
)
async def register_user(db_session: DbSession, user_in: UserCreate):
    """Register user endpoint."""
    try:
        user = await auth_service.register(db_session, user_in)
        return Token(access_token=user.token)
    except UsernameAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    except EmailAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@user_router.get(
    "/", response_model=UserPagination, dependencies=[Depends(get_moderator_user)]
)
async def read_users(db_session: DbSession):
    try:
        users, total = await auth_service.list_users(db_session)
        users_read = [UserRead.model_validate(u) for u in users]
        return UserPagination(itemPerPage=total, page=1, total=total, items=users_read)
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@user_router.get("/me")
async def read_user_me(current_user: CurrentUser) -> UserRead:
    """Me endpoint"""
    return current_user


# @user_router.get(
#     "/me/posts/{post_id}",
#     dependencies=[
#         Depends(
#             PermissionDependency(
#                 {
#                     "posts:read",
#                 }
#             )
#         )
#     ],
# )
# async def read_user_post_id(post_id: int):
#     return {"status": "ok"}
