import pytest

from sqlalchemy.exc import SQLAlchemyError

from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_delete
async def test_delete_driver(repo, init_data):
    drivers_count = await repo.query(Driver).count()
    assert drivers_count == 2

    async with repo:
        driver = await repo.query(Driver).get(id=init_data["ivan"].id)
        await repo.stmt(Driver).delete(driver)

    drivers_count = await repo.query(Driver).count()
    assert drivers_count == 1


@pytest.mark.repo
@pytest.mark.repo_delete
async def test_delete_driver_no_instance(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).delete(None)
