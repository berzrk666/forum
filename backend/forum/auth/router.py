import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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
from forum.config import settings
from forum.database.core import DbSession

auth_router = APIRouter(prefix="/auth", tags=["authorization"])
user_router = APIRouter(prefix="/users", tags=["users"])

log = logging.getLogger(__name__)


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
        user = await auth_service.authenticate(db_session, request, user_in)
        # token = Token(access_token=user.token)
        # return UserLoginResponse(token=token)

        # Store refresh token in cache
        refresh_token = user.refresh_token
        cache_key = f"rf_token:{refresh_token}"
        log.info(cache_key)
        await request.app.state.cache.setex(
            cache_key, settings.JWT_RF_TOKEN_EXPIRATION, user.id
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.JWT_RF_TOKEN_EXPIRATION,
        )
        return Token(access_token=user.token)
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


# HACK: Needs improving
@auth_router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    db_session: DbSession, request: Request, response: Response
):
    try:
        rf_token = request.cookies.get("refresh_token")
        if not rf_token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No refresh token found.")
        user_id = await request.app.state.cache.get(f"rf_token:{rf_token}")

        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token.")

        log.info(user_id)

        user = await auth_service._get(db_session, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")

        # Delete old refresh token from cache
        await request.app.state.cache.delete(f"rf_token:{rf_token}")

        new_refresh = user.refresh_token
        await request.app.state.cache.setex(
            f"rf_token:{new_refresh}", settings.JWT_RF_TOKEN_EXPIRATION, user.id
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.JWT_RF_TOKEN_EXPIRATION,
        )

        return Token(
            access_token=user.token,
        )
    except Exception as e:
        log.error(e)
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
