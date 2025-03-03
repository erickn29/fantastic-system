import pytest

from sqlalchemy.exc import SQLAlchemyError

from tests.apps.tools.repository.v2.conftest import DriverSchema
from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_get_or_none
async def test_get_or_none_driver_by_id(repo, init_data):
    driver = await repo.query(Driver).get_or_none(id=init_data["ivan"].id)
    assert isinstance(driver, Driver)
    assert driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_get_or_none
async def test_get_or_none_driver_by_id_dto(repo, init_data):
    driver = await repo.query(Driver).get_or_none(
        dto=DriverSchema, id=init_data["ivan"].id
    )
    assert isinstance(driver, DriverSchema)
    assert driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_get_or_none
async def test_get_or_none_driver_by_last_name(repo, init_data):
    driver = await repo.query(Driver).get_or_none(last_name=init_data["ivan"].last_name)
    assert isinstance(driver, Driver)
    assert driver.last_name == init_data["ivan"].last_name


@pytest.mark.repo
@pytest.mark.repo_get_or_none
async def test_get_or_none_driver_by_last_name_and_first_name(repo, init_data):
    driver = await repo.query(Driver).get_or_none(
        last_name=init_data["ivan"].last_name,
        first_name=init_data["ivan"].first_name,
    )
    assert isinstance(driver, Driver)
    assert driver.last_name == init_data["ivan"].last_name
    assert driver.first_name == init_data["ivan"].first_name


@pytest.mark.repo
@pytest.mark.repo_get_or_none
async def test_get_or_none_driver_by_wrong_last_name(repo, init_data):
    driver = await repo.query(Driver).get_or_none(last_name="wrong_last_name")
    assert driver is None


@pytest.mark.repo
@pytest.mark.repo_get_or_none
async def test_get_or_none_driver_multiple_instances(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        await repo.query(Driver).get_or_none(patronymic=init_data["ivan"].patronymic)
