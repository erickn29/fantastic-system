import pytest

from sqlalchemy.exc import SQLAlchemyError

from src.app.tools.repository.sql_alchemy.sql_alchemy_v2 import F
from tests.apps.tools.repository.v2.models import Driver, License


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_id(init_data, repo):
    driver = await repo.query(Driver).get(id=init_data["ivan"].id)
    assert isinstance(driver, Driver)
    assert driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_first_name_join_license(init_data, repo):
    driver = await repo.query(Driver).get(
        first_name__ilike=init_data["ivan"].first_name[:3].upper(),
        join__license__number=init_data["ivan_license"].number,
    )
    assert isinstance(driver, Driver)
    assert driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_f_expressions_get_results(init_data, repo):
    driver = await repo.query(Driver).get(
        # no results
        F(
            first_name__ilike=init_data["ivan"].first_name[:3].upper(),
            join__license__number=init_data["ivan_license"].number + 10,
        )
        # no results
        | F(phone_number=init_data["ivan"].phone_number, join__cars__year__gte=2024)
        # get match
        | F(
            join__cars__color__in=["Серый", "Красный"],
        )
    )
    assert isinstance(driver, Driver)
    assert driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_f_expressions_no_results(init_data, repo):
    with pytest.raises(SQLAlchemyError):
        await repo.query(Driver).get(
            # no results
            F(
                first_name__ilike=init_data["ivan"].first_name[:3].upper(),
                join__license__number=init_data["ivan_license"].number + 10,
            )
            # no results
            | F(phone_number=init_data["ivan"].phone_number, join__cars__year__gte=2024)
            # no results
            | F(
                join__cars__color__in=["Бежевый", "Красный"],
            )
        )


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_first_name_join_license_no_result(init_data, repo):
    with pytest.raises(SQLAlchemyError):
        await repo.query(Driver).get(
            first_name=init_data["ivan"].first_name,
            join__license__number=100001,
        )


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_last_name(repo, init_data):
    driver = await repo.query(Driver).get(last_name=init_data["oleg"].last_name)
    assert isinstance(driver, Driver)
    assert driver.last_name == init_data["oleg"].last_name


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_last_name_and_first_name(init_data, repo):
    driver = await repo.query(Driver).get(
        last_name=init_data["ivan"].last_name,
        first_name=init_data["ivan"].first_name,
    )
    assert isinstance(driver, Driver)
    assert driver.last_name == init_data["ivan"].last_name
    assert driver.first_name == init_data["ivan"].first_name


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_id_joined_load_license(init_data, repo):
    driver = await repo.query(Driver).get(
        joined_load=[Driver.license],
        id=init_data["ivan"].id,
    )
    assert isinstance(driver, Driver)
    assert isinstance(driver.license, License)
    assert driver.license.driver_id == driver.id


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_by_id_select_in_load_cars(init_data, repo):
    driver = await repo.query(Driver).get(
        select_in_load=[Driver.cars],
        id=init_data["oleg"].id,
    )
    assert isinstance(driver, Driver)
    assert isinstance(driver.cars, list)
    assert len(driver.cars) == 1
    assert driver.cars[0].driver_id == driver.id


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_no_results(init_data, repo):
    with pytest.raises(SQLAlchemyError):
        await repo.query(Driver).get(last_name="wrong_last_name")


@pytest.mark.repo
@pytest.mark.repo_get
async def test_get_driver_multiple_instances(init_data, repo):
    with pytest.raises(SQLAlchemyError):
        await repo.query(Driver).get(patronymic=init_data["ivan"].patronymic)
