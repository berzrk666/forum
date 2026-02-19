import pytest

from forum.auth.models import User
from forum.category.models import Category
from forum.forum.exceptions import ForumDoesNotExist
from forum.forum.models import Forum
from forum.thread.models import Thread
from forum.thread.schemas import ThreadCreate
from forum.thread.service import ThreadService
from tests.conftest import VALID_EMAIL, VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def thread_service():
    return ThreadService()


@pytest.fixture
async def test_category(test_session):
    f = Category(name="Test Forum", order=1)
    test_session.add(f)
    await test_session.flush()
    return f


@pytest.fixture
async def test_forum(test_session, test_category):
    f = Forum(name="Test Forum", order=1, category=test_category)
    test_session.add(f)
    await test_session.flush()
    return f


class TestThreadServiceCreate:
    async def test_create_thread_success(
        self, thread_service: ThreadService, test_session, test_forum, test_user
    ):
        """A new thread should be created."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id)
        thread = await thread_service.create(test_session, t, test_user)

        assert thread

    async def test_create_thread_info_stored(
        self, thread_service: ThreadService, test_session, test_forum, test_user
    ):
        """Thread info is stored properly"""
        t = ThreadCreate(title="Test", forum_id=test_forum.id)
        thread = await thread_service.create(test_session, t, test_user)

        assert thread.forum == test_forum
        assert thread.title == "Test"

    async def test_thread_tracks_author(
        self, thread_service: ThreadService, test_session, test_forum, test_user
    ):
        """Thread keeps information about who created the thread."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id)
        thread = await thread_service.create(test_session, t, test_user)

        assert thread.author == test_user

    async def test_thread_tracks_forum(
        self, thread_service: ThreadService, test_session, test_forum, test_user
    ):
        """Thread keeps information about which forum it belongs."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id)
        thread = await thread_service.create(test_session, t, test_user)

        assert thread.forum == test_forum

    async def test_create_thread_without_existing_forum(
        self, thread_service: ThreadService, test_session, test_user
    ):
        """
        ForumDoesNotExist is raised when attempting to create a
        Thread without an existing Forum.
        """
        t = ThreadCreate(title="Test", forum_id=1)
        with pytest.raises(ForumDoesNotExist):
            await thread_service.create(test_session, t, test_user)

    async def test_create_thread_with_duplicate_title(
        self, thread_service: ThreadService, test_session, test_forum, test_user
    ):
        """Thread with duplicate name should exist."""
        t = ThreadCreate(title="Test", forum_id=1)
        thread1 = await thread_service.create(test_session, t, test_user)
        t = ThreadCreate(title="Test", forum_id=1)
        thread2 = await thread_service.create(test_session, t, test_user)

        assert thread1
        assert thread2
