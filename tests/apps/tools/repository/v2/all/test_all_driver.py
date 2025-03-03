import pytest

from tests.apps.tools.repository.v2.conftest import (
    DriverSchema,
    DriverWithInLoadsSchema,
)
from tests.apps.tools.repository.v2.models import Driver, License, Route


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_drivers(init_data, repo):
    drivers = await repo.query(Driver).all()
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_routes_empty_result(init_data, repo):
    routes = await repo.query(Route).all()
    assert len(routes) == 0


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_drivers_order_by_created_at_desc(init_data, repo):
    drivers = await repo.query(Driver).all(order_by=[Driver.created_at.desc()])
    assert len(drivers) == 2
    assert drivers[0].id == init_data["oleg"].id
    assert drivers[1].id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_drivers_select_in_load(init_data, repo):
    drivers = await repo.query(Driver).all(select_in_load=[Driver.cars])
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id

    assert len(drivers[0].cars) == 1
    assert len(drivers[1].cars) == 1


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_drivers_joined_load(init_data, repo):
    drivers = await repo.query(Driver).all(joined_load=[Driver.license])
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id

    assert isinstance(drivers[0].license, License)
    assert drivers[1].license is None


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_drivers_dto(init_data, repo):
    drivers = await repo.query(Driver).all(dto=DriverSchema)
    assert len(drivers) == 2
    assert isinstance(drivers[0], DriverSchema)
    assert isinstance(drivers[1], DriverSchema)
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_all
async def test_all_drivers_select_in_load_dto(init_data, repo):
    drivers = await repo.query(Driver).all(
        select_in_load=[Driver.cars],
        joined_load=[Driver.license],
        dto=DriverWithInLoadsSchema,
    )
    assert len(drivers) == 2
    assert isinstance(drivers[0], DriverWithInLoadsSchema)
    assert isinstance(drivers[1], DriverWithInLoadsSchema)
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id

    assert len(drivers[0].cars) == 1
    assert len(drivers[1].cars) == 1
    assert drivers[1].license is None
