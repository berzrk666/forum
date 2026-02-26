import pytest

from forum.category.models import Category
from forum.forum.exceptions import ForumDoesNotExist
from forum.forum.models import Forum
from forum.thread.exception import ThreadDoesNotExist, ThreadNotOwner
from forum.thread.models import Thread
from forum.thread.schemas import ThreadCreate, ThreadEditUser
from forum.thread.service import ThreadService


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


@pytest.fixture
def thread_owner(test_user):
    return test_user


@pytest.fixture
def other_user(test_user2):
    return test_user2


@pytest.fixture
async def new_thread(test_session, test_forum, thread_owner):
    t = Thread(
        title="Test", forum=test_forum, content="test content", author=thread_owner
    )
    test_session.add(t)
    await test_session.flush()
    return t


class TestThreadServiceCreate:
    async def test_create_thread_success(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        """A new thread should be created."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        thread = await thread_service.create(test_session, t, thread_owner)

        assert thread

    async def test_create_thread_info_stored(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        """Thread info is stored properly"""
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        thread = await thread_service.create(test_session, t, thread_owner)

        assert thread.forum == test_forum
        assert thread.title == "Test"

    async def test_thread_tracks_author(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        """Thread keeps information about who created the thread."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        thread = await thread_service.create(test_session, t, thread_owner)

        assert thread.author == thread_owner

    async def test_thread_tracks_forum(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        """Thread keeps information about which forum it belongs."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        thread = await thread_service.create(test_session, t, thread_owner)

        assert thread.forum == test_forum

    async def test_create_thread_without_existing_forum(
        self, thread_service: ThreadService, test_session, thread_owner
    ):
        """
        ForumDoesNotExist is raised when attempting to create a
        Thread without an existing Forum.
        """
        t = ThreadCreate(title="Test", forum_id=1, content="test content")
        with pytest.raises(ForumDoesNotExist):
            await thread_service.create(test_session, t, thread_owner)

    async def test_create_thread_with_duplicate_title(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        """Thread with duplicate name should exist."""
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        thread1 = await thread_service.create(test_session, t, thread_owner)
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        thread2 = await thread_service.create(test_session, t, thread_owner)

        assert thread1
        assert thread2


class TestThreadServiceList:
    async def test_list_one_thread(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)

        threads, total = await thread_service.list_threads(
            test_session, test_forum.id, page=1, limit=2
        )

        assert threads
        assert total
        assert len(threads) == 1

    async def test_list_multiple_threads(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)

        threads, total = await thread_service.list_threads(
            test_session, test_forum.id, page=1, limit=3
        )

        assert len(threads) == 3
        assert total == 3

    async def test_list_empty_returns_empty_list(
        self, thread_service: ThreadService, test_session, test_forum
    ):
        threads, total = await thread_service.list_threads(
            test_session, test_forum.id, page=1, limit=5
        )

        assert threads == []
        assert total == 0

    async def test_list_threads_returns_remaining_items_on_last_page(
        self, thread_service: ThreadService, test_session, test_forum, thread_owner
    ):
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)
        t = ThreadCreate(title="Test", forum_id=test_forum.id, content="test content")
        await thread_service.create(test_session, t, thread_owner)

        threads, total = await thread_service.list_threads(
            test_session, test_forum.id, page=2, limit=2
        )

        assert len(threads) == 1
        assert total == 3

    class TestThreadServiceEdit:
        async def test_user_edit_own_thread(
            self,
            thread_service: ThreadService,
            test_session,
            test_forum,
            thread_owner,
            new_thread,
        ):
            """Tests the user can edit their own thread."""
            t = ThreadEditUser(title="New Title", content="New Content")
            thread = await thread_service.edit(
                test_session, new_thread.id, t, thread_owner
            )

            assert thread

        async def test_user_edit_own_thread_store_new_data(
            self,
            thread_service: ThreadService,
            test_session,
            test_forum,
            thread_owner,
            new_thread,
        ):
            """Tests the new data about the thread is saved after the user edit."""
            t = ThreadEditUser(title="New Title", content="New Content")
            thread = await thread_service.edit(
                test_session, new_thread.id, t, thread_owner
            )

            assert thread.title == "New Title"
            assert thread.content == "New Content"

        async def test_user_edit_only_title(
            self,
            thread_service: ThreadService,
            test_session,
            test_forum,
            thread_owner,
            new_thread,
        ):
            """Should be possible to only edit the title."""
            t = ThreadEditUser(title="New Title")
            old_content = new_thread.content
            thread = await thread_service.edit(
                test_session, new_thread.id, t, thread_owner
            )

            assert thread.title == "New Title"
            assert thread.content == old_content

        async def test_user_edit_only_content(
            self,
            thread_service: ThreadService,
            test_session,
            test_forum,
            thread_owner,
            new_thread,
        ):
            """Should be possible to only edit the title."""
            t = ThreadEditUser(content="New Content")
            old_title = new_thread.title
            thread = await thread_service.edit(
                test_session, new_thread.id, t, thread_owner
            )

            assert thread.title == old_title
            assert thread.content == "New Content"

        async def test_user_cant_edit_others_thread(
            self,
            thread_service: ThreadService,
            test_session,
            test_forum,
            new_thread,
            test_user2,
        ):
            """A user should not be able to edit others thread."""
            t = ThreadEditUser(content="New Content")
            with pytest.raises(ThreadNotOwner):
                await thread_service.edit(test_session, new_thread.id, t, test_user2)

        async def test_cant_edit_non_existent_thread(
            self, thread_service: ThreadService, test_session, test_forum, thread_owner
        ):
            """Cant edit a thread that does not exist."""
            t = ThreadEditUser(content="New Content")
            with pytest.raises(ThreadDoesNotExist):
                await thread_service.edit(test_session, 5, t, thread_owner)
