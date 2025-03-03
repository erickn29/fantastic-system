from datetime import date
from uuid import uuid4

import pytest

from sqlalchemy.exc import SQLAlchemyError

from tests.apps.tools.repository.v2.conftest import DriverSchema
from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_create
async def test_create_driver_correct_data(repo):
    async with repo:
        driver = await repo.stmt(Driver).create(
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+79999999999",
        )

    assert driver is not None
    assert isinstance(driver, Driver)
    assert driver.first_name == "Иван"
    assert driver.last_name == "Петров"
    assert driver.patronymic == "Николаевич"
    assert driver.birth_date == date(1990, 1, 1)
    assert driver.phone_number == "+79999999999"

    driver = await repo.query(Driver).get(phone_number="+79999999999")

    assert isinstance(driver, Driver)
    assert driver.id is not None
    assert driver.first_name == "Иван"
    assert driver.last_name == "Петров"
    assert driver.patronymic == "Николаевич"
    assert driver.birth_date == date(1990, 1, 1)
    assert driver.phone_number == "+79999999999"


@pytest.mark.repo
@pytest.mark.repo_create
async def test_create_driver_duplicate_phone(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).create(
                first_name="Иван",
                last_name="Петров",
                patronymic="Николаевич",
                birth_date=date(1990, 1, 1),
                phone_number="+71234567890",
            )


@pytest.mark.repo
@pytest.mark.repo_create
async def test_create_driver_null_first_name(repo):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).create(
                last_name="Петров",
                patronymic="Николаевич",
                birth_date=date(1990, 1, 1),
                phone_number="+71234567892",
            )


@pytest.mark.repo
@pytest.mark.repo_create
async def test_create_driver_incorrect_first_name_length(repo):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).create(
                first_name=uuid4().hex,
                last_name="Петров",
                patronymic="Николаевич",
                birth_date=date(1990, 1, 1),
                phone_number="+71234567890",
            )


@pytest.mark.repo
@pytest.mark.repo_create
async def test_create_driver_incorrect_first_name_type(repo):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).create(
                first_name=123,
                last_name="Петров",
                patronymic="Николаевич",
                birth_date=date(1990, 1, 1),
                phone_number="+71234567890",
            )


@pytest.mark.repo
@pytest.mark.repo_create
async def test_create_driver_correct_data_dto(repo):
    async with repo:
        driver = await repo.stmt(Driver).create(
            dto=DriverSchema,
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+79999999999",
        )

    assert driver is not None
    assert isinstance(driver, DriverSchema)
    assert driver.first_name == "Иван"
    assert driver.last_name == "Петров"
    assert driver.patronymic == "Николаевич"
    assert driver.birth_date == date(1990, 1, 1)
    assert driver.phone_number == "+79999999999"
