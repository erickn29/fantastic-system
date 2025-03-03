from collections.abc import AsyncGenerator
from datetime import date
from uuid import UUID, uuid4

import pytest

from pydantic import BaseModel, ConfigDict
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.tools.repository.sql_alchemy.sql_alchemy_v2 import SARepository
from core.config import config
from core.database import DatabaseHelper
from tests.apps.tools.repository.v2.base import Base
from tests.apps.tools.repository.v2.models import Car, Driver, License


@pytest.fixture(scope="session")
def database():
    async_db_url = config.db.url(db_name=f"test_db_{uuid4().hex[:5]}")
    db_url = async_db_url.replace("postgresql+asyncpg", "postgresql")
    if not database_exists(db_url):
        create_database(db_url)

    yield async_db_url

    if database_exists(db_url):
        drop_database(db_url.replace("postgresql+asyncpg", "postgresql"))


@pytest.fixture(scope="session")
async def engine(database) -> AsyncGenerator:
    engine = create_async_engine(
        database,
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def run_migrations(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def db_conn(database):
    db_conn = DatabaseHelper(url=database)
    return db_conn


@pytest.fixture(scope="session")
def repo(db_conn):
    return SARepository(db_conn)


@pytest.fixture(scope="function")
async def init_data(repo):
    async with repo:
        ivan = await repo.stmt(Driver).create(
            first_name="Иван",
            last_name="Петров",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 1),
            phone_number="+71234567890",
        )
        oleg = await repo.stmt(Driver).create(
            first_name="Олег",
            last_name="Иванов",
            patronymic="Николаевич",
            birth_date=date(1990, 1, 2),
            phone_number="+71234567891",
        )
        ivan_license = await repo.stmt(License).create(
            driver_id=ivan.id, series=1234, number=456789
        )
        ivan_car = await repo.stmt(Car).create(
            driver_id=ivan.id,
            vendor="Toyota",
            model="Camry",
            year=2022,
            color="Серый",
            is_broken=False,
            cost=200000,
        )
        oleg_car = await repo.stmt(Car).create(
            driver_id=oleg.id,
            vendor="Ford",
            model="Mustang",
            year=2021,
            color="Белый",
            is_broken=True,
            cost=150000,
        )
    return {
        "ivan": ivan,
        "oleg": oleg,
        "ivan_license": ivan_license,
        "ivan_car": ivan_car,
        "oleg_car": oleg_car,
    }


class DriverSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    patronymic: str
    birth_date: date
    phone_number: str


class LicenseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: UUID
    series: int
    number: int


class CarSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: UUID
    vendor: str
    model: str
    year: int
    color: str
    is_broken: bool
    cost: int


class DriverWithInLoadsSchema(DriverSchema):
    license: LicenseSchema | None = None
    cars: list[CarSchema] | None = None
