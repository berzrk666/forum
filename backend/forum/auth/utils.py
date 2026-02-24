from datetime import datetime, timedelta, timezone
import logging
import secrets

from fastapi import Response
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forum.auth.schemas import TokenData
from forum.config import settings

log = logging.getLogger(__name__)


async def init_roles(session: AsyncSession):
    from forum.auth.models import Role

    res = await session.scalar(select(Role))
    if res is None:
        role = Role(name="User")
        session.add(role)
        log.info("Creating User role")
        role = Role(name="Moderator")
        session.add(role)
        log.info("Creating Moderador role")
        role = Role(name="Admin")
        session.add(role)
        log.info("Creating Admin role")
        await session.commit()


def generate_jwt_token(user_id: int, role: str) -> str:
    """Generate a JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION)
    to_encode = TokenData(sub=str(user_id), exp=expire, role=role)

    return jwt.encode(to_encode.model_dump(), settings.JWT_KEY, settings.JWT_ALG)


def generate_refresh_token() -> str:
    """Generate a refresh token."""
    return secrets.token_urlsafe(32)


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
