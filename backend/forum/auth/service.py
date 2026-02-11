import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from forum.auth.exceptions import (
    EmailAlreadyExists,
    UsernameAlreadyExists,
)
from forum.auth.models import User
from forum.auth.schemas import UserCreate

log = logging.getLogger(__name__)


async def create(session: AsyncSession, user_in: UserCreate) -> User:
    """Create a new User in database."""
    user = User(**user_in.model_dump(exclude={"password"}))
    user.set_password(user_in.password)

    try:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user
    except IntegrityError as e:
        detail = str(e.orig)
        if "username" in detail:
            raise UsernameAlreadyExists()
        else:
            raise EmailAlreadyExists()
    except Exception as e:
        log.error(f"Unexpected error when creating {user!r}: {e}")
        raise


async def get(session: AsyncSession, id: int) -> User | None:
    """Returns a User by ID."""
    return await session.get(User, id)


async def get_by_username(session: AsyncSession, username: str) -> User | None:
    """Returns a User by Username."""
    res = await session.execute(select(User).where(User.username == username))
    return res.scalar()
