import pytest

from tests.apps.tools.repository.v2.models import Driver


@pytest.mark.repo
@pytest.mark.repo_exists
async def test_exists_drivers(repo, init_data):
    exists = await repo.query(Driver).exists()
    assert exists is True


@pytest.mark.repo
@pytest.mark.repo_exists
async def test_exists_drivers_with_filters(repo, init_data):
    exists = await repo.query(Driver).exists(last_name=init_data["oleg"].last_name)
    assert exists is True

    exists = await repo.query(Driver).exists(last_name="Doe")
    assert exists is False
