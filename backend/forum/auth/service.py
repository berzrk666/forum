import json
import logging

from argon2.exceptions import VerifyMismatchError
from fastapi import Request
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
from forum.auth.schemas import TokenResponse, UserCreate, UserLogin
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

    async def login(
        self, session: AsyncSession, cache: Redis, user_in: UserLogin
    ) -> TokenResponse:
        """
        Login a user if it exists and their credentials are valid.
        Returns an access token and refresh token.
        """

        try:
            user = await self._authenticate(session, user_in)
            token = user.token
            refresh_token = generate_refresh_token()
            await self._cache_store_refresh_token(cache, refresh_token, user)
            return TokenResponse(access_token=token, refresh_token=refresh_token)
        except Exception as e:
            log.error(e)
            raise

    async def _authenticate(self, session: AsyncSession, user_in: UserLogin) -> User:
        """
        Authenticate user existence and credentials.

        Raise IncorrectPasswordOrUsername if user does not exist
        or credentials are wrong.
        """
        user = await self.get_by_username(session, user_in.username)

        try:
            if user is None:
                raise IncorrectPasswordOrUsername
            user.verify_password(user_in.password)
            return user
        except IncorrectPasswordOrUsername:
            try:
                verify_hash(user_in.password, DUMMY_HASH)
            except:  # noqa
                pass
            raise
        except VerifyMismatchError:
            raise IncorrectPasswordOrUsername
        except Exception as e:
            log.error(f"Error authenticating {user_in}: {e}")
            raise

    async def refresh(self, cache: Redis, refresh_token: str) -> TokenResponse:
        """Validate a refresh token. If valid returns new tokens."""
        user_data = await cache.get(f"{REFRESH_TOKEN_PREFIX}:{refresh_token}")
        if user_data is None:
            raise InvalidRefreshToken

        # Delete old refresh token
        await cache.delete(f"{REFRESH_TOKEN_PREFIX}:{refresh_token}")

        # Save new refresh
        new_refresh = generate_refresh_token()
        await cache.set(
            f"{REFRESH_TOKEN_PREFIX}:{new_refresh}",
            user_data,
            ex=settings.JWT_RF_TOKEN_EXPIRATION,
        )

        user = json.loads(user_data)
        access_token = generate_jwt_token(user["user_id"], user["role"])
        return TokenResponse(access_token=access_token, refresh_token=new_refresh)

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

    async def list_users(
        self, session: AsyncSession, page: int, limit: int
    ) -> tuple[list[User], int]:
        """
        List users paginated.
        Returns a list of users and the total number of users.
        """
        try:
            st = (
                select(User)
                .options(joinedload(User.role))
                .offset((page - 1) * limit)
                .limit(limit)
            )
            count_st = select(func.count()).select_from(User)
            res = await session.scalars(st)
            total = await session.scalar(count_st) or 0

            return res.all(), total  # type: ignore
        except Exception as e:
            log.error("Unexpected error during user listing: ", e)
            raise

    async def _cache_store_refresh_token(self, cache: Redis, refresh_token, user: User):
        """Store refresh token in cache."""
        data = {"user_id": user.id, "role": user.role.name}
        await cache.set(
            f"{REFRESH_TOKEN_PREFIX}:{refresh_token}",
            json.dumps(data),
            ex=settings.JWT_RF_TOKEN_EXPIRATION,
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

    async def get_by_username(
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
