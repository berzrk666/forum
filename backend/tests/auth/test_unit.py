import pytest

from forum.auth.exceptions import (
    EmailAlreadyExists,
    IncorrectPasswordOrUsername,
    InsufficientPermission,
    UsernameAlreadyExists,
)
from forum.auth.models import User
from forum.auth.schemas import UserLogin
from forum.auth.service import AuthService
from tests.conftest import VALID_EMAIL, VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def auth_service():
    return AuthService()


class TestAuthServiceRegister:
    async def test_register_user_success(self, auth_service, test_session, valid_user):
        """Registering a User should be returned"""
        user = await auth_service.register(test_session, valid_user)

        assert user

    async def test_register_user_username_stored(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User's username should be saved"""
        user = await auth_service.register(test_session, valid_user)

        assert user.username == VALID_USERNAME

    async def test_register_user_email_stored(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User's email should be saved"""
        user = await auth_service.register(test_session, valid_user)

        assert user.email == VALID_EMAIL

    async def test_register_user_has_an_id(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User gets an ID"""
        user = await auth_service.register(test_session, valid_user)

        assert user.id is not None

    async def test_register_user_plain_password_not_stored(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User should not store the password in plain text."""
        user = await auth_service.register(test_session, valid_user)

        assert user.password != VALID_PASSWORD

    async def test_register_duplicate_username(
        self, auth_service, test_session, valid_user
    ):
        """register should raise UsernameAlreadyExists"""
        user1 = await auth_service.register(test_session, valid_user)

        assert user1, "A user should be created"

        user2 = valid_user
        user2.email = "newemail@email.com"

        with pytest.raises(UsernameAlreadyExists):
            await auth_service.register(test_session, valid_user)

    async def test_register_duplicate_email(
        self, auth_service, test_session, valid_user
    ):
        """register should raise EmailAlreadyExists"""
        user1 = await auth_service.register(test_session, valid_user)

        assert user1, "A user should be created"

        user2 = valid_user
        user2.username = "com"

        with pytest.raises(EmailAlreadyExists):
            await auth_service.register(test_session, valid_user)


@pytest.fixture
def valid_login() -> UserLogin:
    return UserLogin(username=VALID_USERNAME, password=VALID_PASSWORD)


class TestAuthServiceAuthenticate:
    async def test_authenticate_valid(
        self,
        auth_service: AuthService,
        test_session,
        test_role,
        test_redis,
        mock_request,
        mock_response,
        valid_user,
        valid_login,
    ):
        """User should be returned after authenticated."""
        mock_request.app.state.cache = test_redis
        await auth_service.register(test_session, valid_user)

        user = await auth_service.authenticate(
            test_session, mock_request, mock_response, valid_login
        )

        assert user.username == VALID_USERNAME
        assert user.email == VALID_EMAIL

    async def test_authenticate_wrong_password(
        self,
        auth_service: AuthService,
        test_session,
        mock_request,
        mock_response,
        valid_user,
        valid_login,
    ):
        """IncorrectPasswordOrUsername should be raised for wrong password."""
        await auth_service.register(test_session, valid_user)

        login_data = valid_login
        login_data.password = "wrongpassword"
        with pytest.raises(IncorrectPasswordOrUsername):
            await auth_service.authenticate(
                test_session, mock_request, mock_response, login_data
            )

    async def test_authenticate_wrong_username(
        self,
        auth_service: AuthService,
        test_session,
        mock_request,
        mock_response,
        valid_user,
        valid_login,
    ):
        """IncorrectPasswordOrUsername should be raised for wrong username."""
        await auth_service.register(test_session, valid_user)

        login_data = valid_login
        login_data.username = "wrongusername"
        with pytest.raises(IncorrectPasswordOrUsername):
            await auth_service.authenticate(
                test_session, mock_request, mock_response, login_data
            )

    async def test_authenticate_inexistent(
        self,
        auth_service: AuthService,
        test_session,
        mock_request,
        mock_response,
        valid_login,
    ):
        """IncorrectPasswordOrUsername should be raised for inexistent usernames."""
        with pytest.raises(IncorrectPasswordOrUsername):
            await auth_service.authenticate(
                test_session, mock_request, mock_response, valid_login
            )


class TestAuthAuthorization:
    @pytest.fixture
    def test_request(self, mock_request, test_redis):
        mock_request.state.app.cache = test_redis
        return mock_request

    async def test_authorization_with_sufficient_permissions(
        self, auth_service: AuthService, test_request, test_redis
    ):
        """Check authorization works when the user has one permisson and requires this one permisson."""
        user = User(username=VALID_USERNAME, email=VALID_EMAIL)
        user.id = 1
        user.set_password(VALID_PASSWORD)

        perms = {"posts:read"}

        await test_redis.sadd(f"users_perms:{user.id}", *perms)

        result = await auth_service.check_authorization(test_request, user, perms)

        assert result is True

    async def test_authorization_user_with_multiple_permission_but_requires_only_one(
        self, auth_service: AuthService, test_request, test_redis
    ):
        """Check authorization works when the user has many permissons, but requires only one."""
        user = User(username=VALID_USERNAME, email=VALID_EMAIL)
        user.id = 1
        user.set_password(VALID_PASSWORD)

        perms = {"posts:read", "posts:edit", "posts:create", "posts:delete"}

        await test_redis.sadd(f"users_perms:{user.id}", *perms)

        result = await auth_service.check_authorization(
            test_request, user, {"posts:create"}
        )

        assert result is True

    async def test_authorization_user_with_multiple_permission_and_requires_all(
        self, auth_service: AuthService, test_request, test_redis
    ):
        """Check authorization works when the user has many permissons and requires all of them."""
        user = User(username=VALID_USERNAME, email=VALID_EMAIL)
        user.id = 1
        user.set_password(VALID_PASSWORD)

        perms = {"posts:read", "posts:edit", "posts:create", "posts:delete"}

        await test_redis.sadd(f"users_perms:{user.id}", *perms)

        result = await auth_service.check_authorization(test_request, user, perms)

        assert result is True

    async def test_authorization_user_with_one_wrong_permission(
        self, auth_service: AuthService, test_request, test_redis
    ):
        """Check authorization raise InsufficientPermission when the user have
        only one permission and it's not the required one."""
        user = User(username=VALID_USERNAME, email=VALID_EMAIL)
        user.id = 1
        user.set_password(VALID_PASSWORD)

        perms = {"posts:read"}

        await test_redis.sadd(f"users_perms:{user.id}", *perms)

        with pytest.raises(InsufficientPermission):
            await auth_service.check_authorization(test_request, user, {"posts:edit"})

    async def test_authorization_user_with_multiple_wrong_permissions_one_required(
        self, auth_service: AuthService, test_request, test_redis
    ):
        """Check authorization raise InsufficientPermission when the
        user have multiple permission and neither is the required one."""
        user = User(username=VALID_USERNAME, email=VALID_EMAIL)
        user.id = 1
        user.set_password(VALID_PASSWORD)

        perms = {"posts:read", "posts:edit", "posts:create"}

        await test_redis.sadd(f"users_perms:{user.id}", *perms)

        with pytest.raises(InsufficientPermission):
            await auth_service.check_authorization(test_request, user, {"posts:delete"})

    async def test_authorization_user_with_multiple_wrong_permissions_multiple_required(
        self, auth_service: AuthService, test_request, test_redis
    ):
        """Check authorization raise InsufficientPermission when the
        user have multiple permission and requires multiple permissions"""
        user = User(username=VALID_USERNAME, email=VALID_EMAIL)
        user.id = 1
        user.set_password(VALID_PASSWORD)

        perms = {"posts:read", "posts:edit", "posts:create"}

        await test_redis.sadd(f"users_perms:{user.id}", *perms)

        with pytest.raises(InsufficientPermission):
            await auth_service.check_authorization(
                test_request, user, {"posts:delete", "posts:update"}
            )
