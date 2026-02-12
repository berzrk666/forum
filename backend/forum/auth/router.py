import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from forum.auth.dependencies import CurrentUser
from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    UsernameAlreadyExists,
)
from forum.auth.schemas import (
    Token,
    UserCreate,
    UserCreateResponse,
    UserLogin,
    UserRead,
)
from forum.auth.service import auth as auth_service
from forum.database.core import DbSession

auth_router = APIRouter(prefix="/auth", tags=["authorization"])

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
    "/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(db_session: DbSession, user_in: UserCreate):
    """Register user endpoint."""
    try:
        user = await auth_service.register(db_session, user_in)
        return UserCreateResponse(token=user.token)
    except UsernameAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    except EmailAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@auth_router.get("/me")
async def read_user_me(current_user: CurrentUser) -> UserRead:
    """Me endpoint"""
    return current_user
