import pytest
from forum.auth.schemas import UserCreate
from forum.auth.service import AuthService
from tests.conftest import VALID_EMAIL, VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def auth_service():
    return AuthService()


class TestAuthServiceRegister:
    @pytest.fixture
    def valid_user(self, user_data) -> UserCreate:
        return UserCreate(**user_data)

    async def test_create_user_success(self, auth_service, test_session, valid_user):
        """Registering a User should be returned"""
        user = await auth_service.register(test_session, valid_user)

        assert user

    async def test_create_user_username_stored(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User's username should be saved"""
        user = await auth_service.register(test_session, valid_user)

        assert user.username == VALID_USERNAME

    async def test_create_user_email_stored(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User's email should be saved"""
        user = await auth_service.register(test_session, valid_user)

        assert user.email == VALID_EMAIL

    async def test_create_user_has_an_id(self, auth_service, test_session, valid_user):
        """Registering a User gets an ID"""
        user = await auth_service.register(test_session, valid_user)

        assert user.id is not None

    async def test_create_user_plain_password_not_stored(
        self, auth_service, test_session, valid_user
    ):
        """Registering a User should not store the password in plain text."""
        user = await auth_service.register(test_session, valid_user)

        assert user.password != VALID_PASSWORD
