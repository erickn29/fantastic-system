import pytest

from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
async def test_count_drivers(init_data, repo):
    count = await repo.query(Driver).count()
    assert count == 2


@pytest.mark.repo
async def test_count_drivers_with_filters(init_data, repo):
    count = await repo.query(Driver).count(last_name="Петров")
    assert count == 1
    assert isinstance(count, int)

    count = await repo.query(Driver).count(patronymic="Николаевич")
    assert count == 2

    count = await repo.query(Driver).count(patronymic="Николаевичс")
    assert count == 0
    assert isinstance(count, int)
