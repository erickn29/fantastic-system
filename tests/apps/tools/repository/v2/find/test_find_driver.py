import pytest

from tests.apps.tools.repository.v2.models import Driver, License


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_by_id(repo, init_data):
    driver = await repo.query(Driver).find(id=init_data["ivan"].id)
    assert isinstance(driver, Driver)
    assert driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_by_last_name(repo, init_data):
    driver = await repo.query(Driver).find(last_name=init_data["ivan"].last_name)
    assert isinstance(driver, Driver)
    assert driver.last_name == init_data["ivan"].last_name


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_by_last_name_and_first_name(repo, init_data):
    driver = await repo.query(Driver).find(
        last_name=init_data["ivan"].last_name,
        first_name=init_data["ivan"].first_name,
    )
    assert isinstance(driver, Driver)
    assert driver.last_name == init_data["ivan"].last_name
    assert driver.first_name == init_data["ivan"].first_name


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_by_id_joined_load_license(repo, init_data):
    driver = await repo.query(Driver).find(
        joined_load=[Driver.license],
        id=init_data["ivan"].id,
    )
    assert isinstance(driver, Driver)
    assert isinstance(driver.license, License)
    assert driver.license.driver_id == driver.id


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_by_id_select_in_load_cars(repo, init_data):
    driver = await repo.query(Driver).find(
        select_in_load=[Driver.cars],
        id=init_data["ivan"].id,
    )
    assert isinstance(driver, Driver)
    assert isinstance(driver.cars, list)
    assert len(driver.cars) == 1
    assert driver.cars[0].driver_id == driver.id


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_by_wrong_last_name(repo, init_data):
    driver = await repo.query(Driver).find(last_name="wrong_last_name")
    assert driver is None


@pytest.mark.repo
@pytest.mark.repo_find
async def test_find_driver_multiple_instances(repo, init_data):
    driver = await repo.query(Driver).find(first_name=init_data["ivan"].first_name)
    assert driver is not None
    assert isinstance(driver, Driver)
    assert driver.id == init_data["ivan"].id
