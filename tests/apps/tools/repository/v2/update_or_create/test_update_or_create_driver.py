from datetime import date

import pytest

from sqlalchemy.exc import SQLAlchemyError

from tests.apps.tools.repository.v2.conftest import DriverSchema
from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_update_or_create
async def test_update_or_create_driver_create_true(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).update_or_create(
            {
                "phone_number": "+79999999999",
            },
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+71234567891",
        )
    assert created is True
    assert isinstance(driver, Driver)
    assert driver.phone_number == "+79999999999"


@pytest.mark.repo
@pytest.mark.repo_update_or_create
async def test_update_or_create_driver_create_true_dto(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).update_or_create(
            {
                "phone_number": "+79999999999",
            },
            dto=DriverSchema,
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+71234567891",
        )
    assert created is True
    assert isinstance(driver, DriverSchema)
    assert driver.phone_number == "+79999999999"


@pytest.mark.repo
@pytest.mark.repo_update_or_create
async def test_update_or_create_driver_create_false(repo, init_data):
    async with repo:
        driver, created = await repo.stmt(Driver).update_or_create(
            {
                "phone_number": init_data["ivan"].phone_number,
            },
            first_name="Артем",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+71234567890",
        )
    assert created is False
    assert isinstance(driver, Driver)
    assert driver.phone_number == init_data["ivan"].phone_number
    assert driver.first_name == "Артем"


@pytest.mark.repo
@pytest.mark.repo_update_or_create
async def test_update_or_create_driver_create_error_uq_phone_exists(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).update_or_create(
                {
                    "last_name": "Obama",
                },
                first_name="Артем",
                last_name="Петров",
                patronymic="Николаевич",
                birth_date=date(1990, 1, 1),
                phone_number="+71234567890",
            )
