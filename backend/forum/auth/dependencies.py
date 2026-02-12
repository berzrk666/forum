from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer

from forum.auth.models import User
from forum.auth.service import auth as auth_service
from forum.config import settings
from forum.database.core import DbSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    session: DbSession, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Validate current user"""
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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
