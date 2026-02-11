from datetime import datetime, timezone
import logging

from argon2 import verify_password
from fastapi import APIRouter, HTTPException, Request, status

from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    UsernameAlreadyExists,
)
from forum.auth.schemas import (
    UserCreate,
    UserCreateResponse,
    UserLogin,
    UserLoginResponse,
)
from forum.auth.service import create, get_by_username
from forum.database.core import DbSession

auth_router = APIRouter(prefix="/auth", tags=["authorization"])

log = logging.getLogger(__name__)


@auth_router.post(
    "/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK
)
async def login_endpoint(db_session: DbSession, user_in: UserLogin, request: Request):
    """Login endpoint."""
    try:
        user = await get_by_username(db_session, user_in.username)
        if not user or not (user.verify_password(user_in.password)):
            raise IncorrectPasswordOrUsername
        return UserLoginResponse(token=user.token)
    except IncorrectPasswordOrUsername:
        log.warning(
            f"Failed login attempt for username: {user_in.username} "
            f"from IP: {request.client.host} at {datetime.now(timezone.utc)}"  # type: ignore
        )
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Incorrect Username or Password"
        )
    except Exception as e:
        log.error(f"Error in login: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
        )


@auth_router.post(
    "/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(db_session: DbSession, user_in: UserCreate):
    try:
        user = await create(db_session, user_in)
        log.info(type(user.token))
        return UserCreateResponse(token=user.token)
    except UsernameAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists.")
    except EmailAlreadyExists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists.")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred."
        )
