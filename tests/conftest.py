import asyncio

from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import uuid4

import pytest

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from core.config import config
from model.base import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database(event_loop):
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
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def run_migrations(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_ = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_() as session:  # type: ignore
        yield session


@pytest.fixture(scope="function")
async def mocked_session(session, module_mocker) -> AsyncGenerator[AsyncSession, None]:
    module_mocker.patch("core.database.db_conn.session_factory", return_value=session)
    yield session
