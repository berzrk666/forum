import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordBearer

from forum.auth.exceptions import InsufficientPermission
from forum.auth.models import User
from forum.auth.service import auth as auth_service
from forum.config import settings
from forum.database.core import DbSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

log = logging.getLogger(__name__)

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
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = await auth_service._get(session, user_id)
    if not user:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_moderator_user(current_user: CurrentUser):
    """Validate  if user is at least a moderator."""
    if not current_user.is_moderator():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You must be a moderator")
    return current_user


ModeratorUser = Annotated[User, Depends(get_moderator_user)]


async def get_admin_user(current_user: CurrentUser):
    """Validate  if user is an Admin."""
    if not current_user.is_admin():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You must be an admin")
    return current_user


AdminUser = Annotated[User, Depends(get_admin_user)]


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
