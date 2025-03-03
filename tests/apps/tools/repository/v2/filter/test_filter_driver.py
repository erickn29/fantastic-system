from datetime import date

import pytest

from src.app.tools.repository.sql_alchemy.sql_alchemy_v2 import F
from tests.apps.tools.repository.v2.conftest import DriverSchema
from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_exact(repo, init_data):
    drivers = await repo.query(Driver).filter(first_name="Иван", last_name="Петров")
    assert len(drivers) == 1
    assert drivers[0].id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_not_exact(repo, init_data):
    drivers = await repo.query(Driver).filter(first_name__not_exact="Иван")
    assert len(drivers) == 1
    assert drivers[0].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_gt(repo, init_data):
    drivers = await repo.query(Driver).filter(birth_date__gt=date(1990, 1, 1))
    assert len(drivers) == 1
    assert drivers[0].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_gte(repo, init_data):
    drivers = await repo.query(Driver).filter(birth_date__gte=date(1990, 1, 1))
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_lt(repo, init_data):
    drivers = await repo.query(Driver).filter(birth_date__lt=date(1990, 1, 2))
    assert len(drivers) == 1
    assert drivers[0].id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_lte(repo, init_data):
    drivers = await repo.query(Driver).filter(birth_date__lte=date(1990, 1, 2))
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_lt_gt(repo, init_data):
    drivers = await repo.query(Driver).filter(
        birth_date__lt=date(1990, 1, 3),
        birth_date__gt=date(1990, 1, 1),
    )
    assert len(drivers) == 1
    assert drivers[0].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_in(repo, init_data):
    drivers = await repo.query(Driver).filter(last_name__in=["Петров", "Иванов"])
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_not_in(repo, init_data):
    drivers = await repo.query(Driver).filter(last_name__not_in=["Иванова", "Иванов"])
    assert len(drivers) == 1
    assert drivers[0].id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_like(repo, init_data):
    drivers = await repo.query(Driver).filter(patronymic__like="Нико")
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_like_dto(repo, init_data):
    drivers = await repo.query(Driver).filter(patronymic__like="Нико", dto=DriverSchema)
    assert len(drivers) == 2
    assert isinstance(drivers[0], DriverSchema)
    assert isinstance(drivers[1], DriverSchema)
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_ilike(repo, init_data):
    drivers = await repo.query(Driver).filter(patronymic__ilike="нико")
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_between(repo, init_data):
    drivers = await repo.query(Driver).filter(
        birth_date__between=(date(1990, 1, 1), date(1990, 2, 2))
    )
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_limit_offset(repo, init_data):
    drivers = await repo.query(Driver).filter(
        limit=2, offset=0, birth_date__gt=date(1989, 1, 1)
    )
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id

    drivers = await repo.query(Driver).filter(
        limit=1, offset=0, birth_date__gt=date(1989, 1, 1)
    )
    assert len(drivers) == 1
    assert drivers[0].id == init_data["ivan"].id

    drivers = await repo.query(Driver).filter(
        limit=1, offset=1, birth_date__gt=date(1989, 1, 1)
    )
    assert len(drivers) == 1
    assert drivers[0].id == init_data["oleg"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_filter_driver_gte_with_join(repo, init_data):
    drivers = await repo.query(Driver).filter(
        birth_date__gte=date(1990, 1, 1),
        join__cars__year__gte=2022,
    )
    assert len(drivers) == 1
    assert drivers[0].id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_f_filters(repo, init_data):
    drivers = await repo.query(Driver).filter(
        F(
            last_name__in=["Петров", "Сидоров"],
        )
        | F(
            birth_date__lt=date(1990, 1, 1),
        )
    )
    assert len(drivers) == 1
    assert drivers[0].id == init_data["ivan"].id


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_f_filters_no_results(repo, init_data):
    drivers = await repo.query(Driver).filter(
        F(
            last_name__in=["Сергеев", "Сидоров"],
        )
        | F(
            birth_date__lt=date(1990, 1, 1),
        )
    )
    assert len(drivers) == 0


@pytest.mark.repo
@pytest.mark.repo_filter
async def test_f_filters_multi_f(repo, init_data):
    drivers = await repo.query(Driver).filter(
        F(
            last_name__in=["Сергеев", "Сидоров"],
        )
        | F(
            birth_date__lt=date(1990, 1, 1),
        )
        | F(
            first_name__in=["Иван", "Олег"],
        )
    )
    assert len(drivers) == 2
    assert drivers[0].id == init_data["ivan"].id
    assert drivers[1].id == init_data["oleg"].id
