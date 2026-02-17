import pytest
from sqlalchemy.exc import IntegrityError

from forum.category.schemas import CategoryCreate
from forum.category.service import CategoryService
from forum.forum.exceptions import CategoryDoesNotExist
from forum.forum.schemas import ForumCreate
from forum.forum.service import ForumService


@pytest.fixture()
def forum_service():
    return ForumService()


@pytest.fixture()
async def test_category(test_session):
    cat = CategoryCreate(name="General", order=1)
    return await CategoryService().create(test_session, cat)


class TestForumServiceCreate:
    async def test_create_forum_success(
        self, forum_service: ForumService, test_session, test_category
    ):
        """A new Forum should be returned."""
        sample = ForumCreate(
            name="Forum", description="Cool forum", order=1, category_id=1
        )
        forum = await forum_service.create(test_session, sample)
        assert forum

    async def test_create_forum_all_info_stored(
        self, forum_service: ForumService, test_session, test_category
    ):
        """All data about a new forum should be safely stored."""
        sample = ForumCreate(
            name="Forum", description="Cool forum", order=1, category_id=1
        )
        forum = await forum_service.create(test_session, sample)
        assert forum.id == 1
        assert forum.order == 1
        assert forum.description == sample.description
        assert forum.name == sample.name
        assert forum.category.name == "General"

    async def test_create_forum_without_existing_category(
        self, forum_service: ForumService, test_session
    ):
        """A forum should not be created when the category specified does not exist."""
        sample = ForumCreate(
            name="Forum", description="Cool forum", order=1, category_id=1
        )
        with pytest.raises(CategoryDoesNotExist):
            await forum_service.create(test_session, sample)

    async def test_create_forum_without_order_in_empty_db(
        self, forum_service: ForumService, test_session, test_category
    ):
        """A forum should be created with order 1."""
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)

        forum = await forum_service.create(test_session, sample)
        assert forum.order == 1

    async def test_create_forum_without_order(
        self, forum_service: ForumService, test_session, test_category
    ):
        """A forum should be created with the current max order in db + 1 ."""
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        await forum_service.create(test_session, sample)
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        await forum_service.create(test_session, sample)
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        forum = await forum_service.create(test_session, sample)
        assert forum.order == 3

    async def test_create_duplicate_order_fails(
        self, forum_service: ForumService, test_session, test_category
    ):
        """No forum should be created if the order already exists."""
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        await forum_service.create(test_session, sample)
        sample = ForumCreate(
            name="Forum", description="Cool forum", order=1, category_id=1
        )
        with pytest.raises(IntegrityError):
            await forum_service.create(test_session, sample)

    async def test_create_duplicate_name_works(
        self, forum_service: ForumService, test_session, test_category
    ):
        """No forum should be created if the order already exists."""
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        forum1 = await forum_service.create(test_session, sample)
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        forum2 = await forum_service.create(test_session, sample)

        assert forum1.name == forum2.name


class TestForumServiceList:
    async def test_empty_list(self, forum_service: ForumService, test_session):
        """Empty list should be returned."""
        forums = await forum_service.list(test_session)
        assert forums == []

    async def test_list_one_forum(
        self, forum_service: ForumService, test_session, test_category
    ):
        """List with one forum should be returned."""
        sample = ForumCreate(
            name="Forum", description="Cool forum", order=1, category_id=1
        )
        await forum_service.create(test_session, sample)

        forums = await forum_service.list(test_session)
        assert len(forums) == 1

    async def test_list_multiple_forums(
        self, forum_service: ForumService, test_session, test_category
    ):
        """List with multiple forums should be returned."""
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        await forum_service.create(test_session, sample)
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        await forum_service.create(test_session, sample)
        sample = ForumCreate(name="Forum", description="Cool forum", category_id=1)
        await forum_service.create(test_session, sample)

        forums = await forum_service.list(test_session)
        assert len(forums) == 3

    async def test_list_all_information_shown(
        self, forum_service: ForumService, test_session, test_category
    ):
        """List with one forum should be returned."""
        sample = ForumCreate(
            name="Forum", description="Cool forum", order=1, category_id=1
        )
        await forum_service.create(test_session, sample)

        forums = await forum_service.list(test_session)
        assert len(forums) == 1
        assert forums[0].name == "Forum"
        assert forums[0].category.id == 1
        assert forums[0].category.name == "General"
