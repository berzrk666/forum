import logging
import json
from datetime import datetime, timezone

from argon2.exceptions import VerifyMismatchError
from fastapi import Request, Response
from redis.asyncio import Redis
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import select

from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    InsufficientPermission,
    InvalidRefreshToken,
    UsernameAlreadyExists,
)
from forum.auth.models import User, hash_password, verify_hash
from forum.auth.schemas import UserCreate, UserLogin
from forum.auth.utils import generate_jwt_token, generate_refresh_token
from forum.config import settings

log = logging.getLogger(__name__)

DUMMY_HASH = hash_password("dummypassword")

REFRESH_TOKEN_PREFIX = "rf_token"


class AuthService:
    async def register(self, session: AsyncSession, user_in: UserCreate) -> User:
        """Register a new User."""
        user = User(**user_in.model_dump(exclude={"password"}))
        user.set_password(user_in.password)
        user.role_id = 1  # TODO: remove hardcode

        return await self._create(session, user)

    async def authenticate(
        self,
        session: AsyncSession,
        request: Request,
        response: Response,
        user_in: UserLogin,
    ) -> User:
        """
        Authenticate a User by their username. Returns the authenticated user.

        Raises IncorrectPasswordOrUsername in case the username
        does not exist or the password is incorrect.
        """
        try:
            user = await self._get_by_username(session, user_in.username)
            if not user:
                raise IncorrectPasswordOrUsername
            user.verify_password(user_in.password)

            # Create refresh token
            refresh_token = generate_refresh_token()
            log.debug(f"Generated the following refresh_token: {refresh_token}")
            await self._cache_store_refresh_token(
                request.app.state.cache,
                refresh_token,
                {"user_id": user.id, "role": user.role.name},
            )

            log.debug("OK. Stored the refresh token in cache.")

            self._set_cookie_refresh_token(response, refresh_token)

            return user
        except IncorrectPasswordOrUsername:
            log.warning(
                f"Failed login attempt with non-existent username: {user_in.username}"
                f"from IP: {request.client.host} at {datetime.now(timezone.utc)}"  # type: ignore
            )
            try:
                verify_hash(user_in.password, DUMMY_HASH)
            except:  # noqa
                pass
            raise IncorrectPasswordOrUsername

        except VerifyMismatchError:
            log.warning(
                f"Failed login attempt with wrong password for username: {user_in.username} "
                f"from IP: {request.client.host} at {datetime.now(timezone.utc)}"  # type: ignore
            )
            raise IncorrectPasswordOrUsername
        except Exception as e:
            log.error(f"Error authenticating {user_in}: {e}")
            raise

    async def refresh_authenticate(
        self, request: Request, response: Response, refresh_token: str
    ) -> str:
        """Authenticate a User by a refresh token. Returns a new access token."""
        cache_db = request.app.state.cache

        user_data = await cache_db.get(f"{REFRESH_TOKEN_PREFIX}:{refresh_token}")
        log.debug(f"{user_data = }")
        if not user_data:
            raise InvalidRefreshToken

        # Delete old refresh
        log.debug("Delete old refresh {REFRESH_TOKEN_PREFIX}:{refresh_token}")
        await cache_db.delete(f"{REFRESH_TOKEN_PREFIX}:{refresh_token}")

        # Save new refresh
        new_refresh = generate_refresh_token()
        await cache_db.set(
            f"{REFRESH_TOKEN_PREFIX}:{new_refresh}",
            user_data,
            ex=settings.JWT_RF_TOKEN_EXPIRATION,
        )

        self._set_cookie_refresh_token(response, new_refresh)

        user = json.loads(user_data)
        return generate_jwt_token(user["user_id"], user["role"])

    async def check_authorization(
        self, request: Request, user: User, permissions: set[str]
    ):
        """Validate if the user has authozitation."""
        try:
            user_perms = await self._get_permissions(request.state.app.cache, user)
        except Exception as e:
            log.error(f"Unexpected error when checking authorization for {user}: {e}")
            raise

        if user_perms and permissions <= user_perms:
            return True
        raise InsufficientPermission

    async def list_users(self, session: AsyncSession) -> tuple[list[User], int]:
        """List all users."""
        try:
            st = select(User).options(joinedload(User.role))
            count_st = select(func.count()).select_from(User)
            res = await session.scalars(st)
            total = await session.scalar(count_st) or 0

            return (res.all(), total)  # type: ignore
        except Exception as e:
            log.error("Unexpected error during user listing: ", e)
            raise

    async def _cache_store_refresh_token(
        self, cache: Redis, refresh_token, user_data: dict
    ):
        """Store refresh token in cache."""
        log.debug(
            f"SET {REFRESH_TOKEN_PREFIX}:{refresh_token} = {json.dumps(user_data)}"
        )
        await cache.set(
            f"{REFRESH_TOKEN_PREFIX}:{refresh_token}",
            json.dumps(user_data),
            ex=settings.JWT_RF_TOKEN_EXPIRATION,
        )

    def _set_cookie_refresh_token(self, response: Response, refresh_token: str):
        """Set the refresh token cookie in the response."""
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.JWT_RF_TOKEN_EXPIRATION,
        )

    async def _get(self, session: AsyncSession, id: int) -> User | None:
        """Returns a User by ID."""
        return await session.get(User, id, options=[joinedload(User.role)])

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
        res = await session.execute(
            select(User).where(User.username == username).options(joinedload(User.role))
        )
        return res.scalar()

    async def _create(self, session: AsyncSession, user: User) -> User:
        """Create a new User in database."""
        try:
            session.add(user)
            await session.flush()
            await session.refresh(user, ["role"])
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
