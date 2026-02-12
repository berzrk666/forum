import logging
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    UsernameAlreadyExists,
)
from forum.auth.models import User
from forum.auth.schemas import UserCreate, UserLogin

log = logging.getLogger(__name__)


class AuthService:
    async def register(self, session: AsyncSession, user_in: UserCreate) -> User:
        """Register a new User."""
        user = User(**user_in.model_dump(exclude={"password"}))
        user.set_password(user_in.password)

        return await self._create(session, user)

    async def authenticate(
        self, session: AsyncSession, request: Request, user_in: UserLogin
    ) -> User:
        """
        Authenticate a User by their username.

        Raises IncorrectPasswordOrUsername in case the username
        does not exist or the password is incorrect.
        """
        try:
            user = await self._get_by_username(session, user_in.username)
            if not user or not (user.verify_password(user_in.password)):
                log.warning(
                    f"Failed login attempt for username: {user_in.username} "
                    f"from IP: {request.client.host} at {datetime.now(timezone.utc)}"  # type: ignore
                )
                raise IncorrectPasswordOrUsername
            return user
        except Exception as e:
            log.error(f"Error authenticating {user_in}: {e}")
            raise

    async def _get(self, session: AsyncSession, id: int) -> User | None:
        """Returns a User by ID."""
        return await session.get(User, id)

    async def _get_by_username(
        self, session: AsyncSession, username: str
    ) -> User | None:
        """Returns a User by Username."""
        res = await session.execute(select(User).where(User.username == username))
        return res.scalar()

    async def _create(self, session: AsyncSession, user: User) -> User:
        """Create a new User in database."""
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


auth = AuthService()
