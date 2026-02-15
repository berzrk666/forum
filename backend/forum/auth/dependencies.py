from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from forum.auth.exceptions import InsufficientPermission
from forum.auth.models import User
from forum.auth.service import auth as auth_service
from forum.config import settings
from forum.database.core import DbSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


credentials_exception = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    session: DbSession, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Validate current user"""
    try:
        payload = jwt.decode(token, settings.JWT_KEY, algorithms=[settings.JWT_ALG])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = await auth_service._get_by_username(session, username)
    if not user:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def moderator_user(current_user: CurrentUser):
    """Validate  if user is at least a moderator."""
    if current_user.role.name in ["Moderator", "Admin"]:
        return current_user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You must be a moderator")


ModeratorUser = Annotated[User, Depends(moderator_user)]


async def admin_user(current_user: CurrentUser):
    """Validate  if user is an Admin."""
    if current_user.role.name == "Admin":
        return current_user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You must be an admin")


ModeratorUser = Annotated[User, Depends(admin_user)]


class PermissionDependency:
    """Check if User has a set of permissions as dependency."""

    def __init__(self, permissions: set[str]) -> None:
        self._perm = permissions

    async def __call__(self, request: Request, user: CurrentUser):
        try:
            await auth_service.check_authorization(request, user, self._perm)
        except InsufficientPermission:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Insufficient Permissions"
            )
        except Exception:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected error occurred"
            )
