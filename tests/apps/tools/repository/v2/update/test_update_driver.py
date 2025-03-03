import uuid

import pytest

from sqlalchemy.exc import SQLAlchemyError

from tests.apps.tools.repository.v2.conftest import DriverSchema
from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_update
async def test_update_driver(repo, init_data):
    async with repo:
        await repo.stmt(Driver).update(
            init_data["ivan"],
            first_name="Джонни",
            last_name="Сильверхэнд",
        )
        updated_driver = await repo.query(Driver).get(id=init_data["ivan"].id)

    assert isinstance(updated_driver, Driver)
    assert updated_driver.first_name == "Джонни"
    assert updated_driver.last_name == "Сильверхэнд"
    assert updated_driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_update
async def test_update_driver_dto(repo, init_data):
    async with repo:
        updated_driver = await repo.stmt(Driver).update(
            instance=init_data["ivan"],
            dto=DriverSchema,
            first_name="Джонни",
            last_name="Сильверхэнд",
        )

    assert isinstance(updated_driver, DriverSchema)
    assert updated_driver.first_name == "Джонни"
    assert updated_driver.last_name == "Сильверхэнд"
    assert updated_driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_update
async def test_update_driver_wrong_attribute(repo, init_data):
    async with repo:
        await repo.stmt(Driver).update(
            init_data["ivan"],
            first_name_wrong="Джонни",
            last_name="Сильверхэнд",
        )
    updated_driver = await repo.query(Driver).get(id=init_data["ivan"].id)
    assert isinstance(updated_driver, Driver)
    assert updated_driver.first_name == init_data["ivan"].first_name
    assert updated_driver.last_name == "Сильверхэнд"
    assert updated_driver.id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_update
async def test_update_driver_none_attribute(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).update(
                init_data["ivan"],
                first_name=None,
                last_name="Сильверхэнд",
            )


@pytest.mark.repo
@pytest.mark.repo_update
async def test_update_driver_set_bad_lenght_first_name(repo, init_data):
    with pytest.raises(SQLAlchemyError):
        async with repo:
            await repo.stmt(Driver).update(
                init_data["ivan"],
                first_name=str(uuid.uuid4().hex),
                last_name="Сильверхэнд",
            )
