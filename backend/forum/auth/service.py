import logging
from datetime import datetime, timezone

from argon2.exceptions import VerifyMismatchError
from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from redis.asyncio import Redis

from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    InsufficientPermission,
    UsernameAlreadyExists,
)
from forum.auth.models import User, hash_password, verify_hash
from forum.auth.schemas import UserCreate, UserLogin

log = logging.getLogger(__name__)

DUMMY_HASH = hash_password("dummypassword")


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
            if not user:
                verify_hash(user_in.password, DUMMY_HASH)
                log.warning(
                    f"Failed login attempt with non-existent username: {user_in.username}"
                    f"from IP: {request.client.host} at {datetime.now(timezone.utc)}"  # type: ignore
                )
                raise IncorrectPasswordOrUsername
            user.verify_password(user_in.password)
            return user
        except VerifyMismatchError:
            log.warning(
                f"Failed login attempt with wrong password for username: {user_in.username} "
                f"from IP: {request.client.host} at {datetime.now(timezone.utc)}"  # type: ignore
            )
            raise IncorrectPasswordOrUsername
        except Exception as e:
            log.error(f"Error authenticating {user_in}: {e}")
            raise

    async def check_authorization(
        self, request: Request, user: User, permissions: set[str]
    ):
        """Validate if the user has authozitation."""
        try:
            user_perms = await self._get_permissions(request.state.app.cache, user)
            if user_perms and permissions <= user_perms:
                return True
            raise InsufficientPermission
        except Exception as e:
            log.error(f"Unexpected error when checking authorization for {user}: {e}")
            raise

    async def _get(self, session: AsyncSession, id: int) -> User | None:
        """Returns a User by ID."""
        return await session.get(User, id)

    async def _get_permissions(self, cache: Redis, user: User) -> set[str] | None:
        """
        Attempt permissions retrieval from cache.
        Otherwise retrieve from database and update cache.
        """
        cache_key = f"users_perms:{user.id}"

        perms = await cache.smembers(cache_key)  # type:ignore
        if perms:
            return perms

        # Cache miss -> Retrive from database
        # TODO: retrieve from database

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
