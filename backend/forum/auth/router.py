import logging
import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic import PositiveInt

from forum.auth.dependencies import (
    CurrentUser,
    get_moderator_user,
)
from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    InvalidRefreshToken,
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
from forum.config import settings
from forum.database.core import DbSession

auth_router = APIRouter(prefix="/auth", tags=["authorization"])
user_router = APIRouter(prefix="/users", tags=["users"])

log = logging.getLogger(__name__)


def set_cookie_refresh_token(response: Response, refresh_token: str):
    """Set the refresh token cookie in the response."""
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.JWT_RF_TOKEN_EXPIRATION,
    )


@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_endpoint(
    db_session: DbSession,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    response: Response,
):
    """Login endpoint."""
    try:
        user_in = UserLogin(username=user_data.username, password=user_data.password)
        tokens = await auth_service.login(db_session, request.app.state.cache, user_in)
        set_cookie_refresh_token(response, tokens.refresh_token)
        return Token(access_token=tokens.access_token)
    except IncorrectPasswordOrUsername:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        log.error(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@auth_router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(request: Request, response: Response):
    rf_token = request.cookies.get("refresh_token")
    if not rf_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No refresh token found.")

    try:
        tokens = await auth_service.refresh(request.app.state.cache, rf_token)
        set_cookie_refresh_token(response, tokens.refresh_token)
        return Token(access_token=tokens.access_token)
    except InvalidRefreshToken:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token.")
    except Exception as e:
        log.error(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@auth_router.post(
    "/register", response_model=Token, status_code=status.HTTP_201_CREATED
)
async def register_user(db_session: DbSession, user_in: UserCreate, request: Request):
    """Register user endpoint."""
    try:
        user = await auth_service.register(db_session, user_in, request.app.state.cache)
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
async def read_users(
    db_session: DbSession, page: PositiveInt = 1, limit: PositiveInt = 10
):
    try:
        users, total = await auth_service.list_users(db_session, page, limit)
        users_read = [UserRead.model_validate(u) for u in users]
        page_size = len(users)
        return UserPagination(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=math.ceil(total / limit) if total > 0 else 0,
            data=users_read,
        )
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
