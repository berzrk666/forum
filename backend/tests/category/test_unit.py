import pytest

from forum.category.exceptions import CategoryAlreadyExists
from forum.category.schemas import CategoryCreate
from forum.category.service import CategoryService


@pytest.fixture()
def cat_service():
    return CategoryService()


class TestCategoryServiceCreate:
    async def test_create_category_success(
        self, cat_service: CategoryService, test_session
    ):
        """Creating a new Category should be returned."""
        sample = CategoryCreate(name="General", order=1)
        cat = await cat_service.create(test_session, sample)

        assert cat

    async def test_category_name_registered(
        self, cat_service: CategoryService, test_session
    ):
        """Creating a new category gets its name saved."""
        sample = CategoryCreate(name="General", order=1)
        cat = await cat_service.create(test_session, sample)

        assert cat.name == "General"

    async def test_category_order_registered(
        self, cat_service: CategoryService, test_session
    ):
        """Creating a new category gets its order stored."""
        sample = CategoryCreate(name="General", order=1)
        cat = await cat_service.create(test_session, sample)

        assert cat.order == 1

    async def test_category_without_specifying_order_empty_db(
        self, cat_service: CategoryService, test_session
    ):
        """Creating a new category without specifying an order should get its own order."""
        sample = CategoryCreate(name="General")
        cat = await cat_service.create(test_session, sample)

        assert cat
        assert cat.order == 1

    async def test_category_without_specifying_order_non_empty_db(
        self, cat_service: CategoryService, test_session
    ):
        """Creating a new category without specifying an order should get its own order."""
        sample = CategoryCreate(name="General")
        cat = await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General1")
        cat = await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General2")
        cat = await cat_service.create(test_session, sample)

        assert cat
        assert cat.order == 3

    async def test_category_with_duplicate_name(
        self, cat_service: CategoryService, test_session
    ):
        """Creating a new category with an already existing name should raise CategoryAlreadyExists."""
        sample = CategoryCreate(name="General", order=1)
        await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General", order=1)

        with pytest.raises(CategoryAlreadyExists):
            await cat_service.create(test_session, sample)


class TestCategoryServiceList:
    async def test_list_success_one_category(
        self, cat_service: CategoryService, test_session
    ):
        """A list with only one category should be correctly returned."""
        sample = CategoryCreate(name="General", order=1)
        await cat_service.create(test_session, sample)

        res = await cat_service.list(test_session)

        assert res
        assert len(res) == 1

    async def test_list_success_multiple_categories(
        self, cat_service: CategoryService, test_session
    ):
        """A list with only one category should be correctly returned."""
        sample = CategoryCreate(name="General")
        await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General1")
        await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General2")
        await cat_service.create(test_session, sample)

        res = await cat_service.list(test_session)

        assert res
        assert len(res) == 3

    async def test_list_empty(self, cat_service: CategoryService, test_session):
        """An empty list should be returned."""
        res = await cat_service.list(test_session)

        assert res == []

    async def test_list_order(self, cat_service: CategoryService, test_session):
        """The list returned should respect the category order."""
        sample = CategoryCreate(name="General3", order=3)
        await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General2", order=2)
        await cat_service.create(test_session, sample)
        sample = CategoryCreate(name="General", order=1)
        await cat_service.create(test_session, sample)

        res = await cat_service.list(test_session)
        assert res
        assert len(res) == 3
        assert res[0].order == 1
        assert res[-1].order == 3
