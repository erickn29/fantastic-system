from datetime import date

import pytest

from sqlalchemy.exc import SQLAlchemyError

from tests.apps.tools.repository.v2.conftest import DriverSchema
from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_get_or_create
async def test_get_or_create_driver_create_true(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).get_or_create(
            [
                "phone_number",
            ],
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+79999999999",
        )
        assert created is True
        assert isinstance(driver, Driver)
        assert driver.phone_number == "+79999999999"


@pytest.mark.repo
@pytest.mark.repo_get_or_create
async def test_get_or_create_driver_create_true_dto(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).get_or_create(
            [
                "phone_number",
            ],
            dto=DriverSchema,
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+79999999999",
        )
        assert created is True
        assert isinstance(driver, DriverSchema)
        assert driver.phone_number == "+79999999999"


@pytest.mark.repo
@pytest.mark.repo_get_or_create
async def test_get_or_create_driver_create_false(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).get_or_create(
            [
                "phone_number",
            ],
            first_name="Артем",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+71234567890",
        )
    assert created is False
    assert isinstance(driver, Driver)
    assert driver.phone_number == init_data["ivan"].phone_number
    assert driver.first_name == init_data["ivan"].first_name


@pytest.mark.repo
@pytest.mark.repo_get_or_create
async def test_get_or_create_driver_create_error_uq_phone_exists(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).get_or_create(
                ["phone_number", "first_name"],
                first_name="Артем",
                last_name="Петров",
                patronymic="Николаевич",
                birth_date=date(1990, 1, 1),
                phone_number="+71234567890",
            )


@pytest.mark.repo
@pytest.mark.repo_get_or_create
async def test_get_or_create_driver_create_without_filters_create_true(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).get_or_create(
            [],
            first_name="Артем",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+71234567893",
        )
    assert created is True
    assert isinstance(driver, Driver)


@pytest.mark.repo
@pytest.mark.repo_get_or_create
async def test_get_or_create_driver_create_without_filters_create_false(
    repo, init_data
):
    async with repo:
        driver, created = await repo.stmt(Driver).get_or_create(
            [],
            first_name=init_data["ivan"].first_name,
            last_name=init_data["ivan"].last_name,
            patronymic=init_data["ivan"].patronymic,
            birth_date=init_data["ivan"].birth_date,
            phone_number=init_data["ivan"].phone_number,
        )
    assert created is False
    assert isinstance(driver, Driver)
