from shutil import rmtree
from typing import AsyncIterator, Sequence

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Cookies
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

import models
import tests.factory as data_factory
from core.dependency import get_async_session
from core.security import create_access_token
from core.settings import config
from main import app
from tests.utils import async_tmp_database


@pytest.fixture(scope="package")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="package", name="pg_url")
def pg_url_fixture() -> str:
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    config.DB_HOST = "localhost"
    return config.async_dsn  # type: ignore


@pytest.fixture(scope="package", autouse=True, name="postgres_temlate")
async def postgres_temlate_fixture(pg_url: str) -> AsyncIterator[str]:
    """
    Creates empty template database with migrations.
    """
    async with async_tmp_database(pg_url, db_name="api_template") as tmp_url:
        engine = create_async_engine(tmp_url)
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        await engine.dispose()
        yield tmp_url


@pytest.fixture(name="postgres")
async def postgres_fixture(postgres_temlate: str) -> AsyncIterator[str]:
    """
    Creates empty temporary database.
    """
    async with async_tmp_database(
        postgres_temlate, suffix="api", template="api_template"
    ) as tmp_url:
        yield tmp_url


@pytest.fixture(name="postgres_engine")
async def postgres_engine_fixture(postgres: str) -> AsyncIterator[AsyncEngine]:
    """
    SQLAlchemy async engine, bound to temporary database.
    """
    engine = create_async_engine(postgres, echo=True)  # type: ignore
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(name="async_session")
async def async_session_fixture(
    postgres_engine: AsyncEngine,
) -> AsyncIterator[AsyncSession]:
    """
    SQLAlchemy session bound to temporary database
    """
    async with AsyncSession(postgres_engine) as session:
        yield session


@pytest.fixture(name="test_app")
async def test_app_fixture(async_session: AsyncSession):
    app.dependency_overrides[get_async_session] = lambda: async_session
    yield app
    app.dependency_overrides = {}


@pytest.fixture(name="client")
async def client_fixture(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """
    TestClient for FastAPI
    """

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(name="factory")
async def factory_fixture(
    async_session: AsyncSession,
) -> data_factory.FactoryCallback:
    """
    Create factory data
    """

    async def _factory(
        model_factory: data_factory.TypeFactory, *args, **kwargs
    ) -> models.MODEL | Sequence[models.MODEL]:
        factory_ = model_factory(async_session)
        await factory_.generate_data(*args, **kwargs)
        return await factory_.commit()

    return _factory


@pytest.fixture(name="admin_client")
async def admin_client_fixture(
    factory: data_factory.FactoryCallback, test_app: FastAPI
):

    user = await factory(
        data_factory.UserFactory,
        password="password123",
        email="test-admin@email.org",
        role=models.RoleChoice.ADMIN,
    )
    assert not isinstance(user, Sequence)
    token = create_access_token({"user_email": user.email})
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        cookie = Cookies()
        cookie.set(config.COOKIE_NAME, token)
        ac.cookies = cookie
        yield ac


@pytest.fixture(name="user_client")
async def user_client_fixture(
    factory: data_factory.FactoryCallback, test_app: FastAPI
):

    user = await factory(
        data_factory.UserFactory,
        password="password123",
        email="test-user@email.org",
        role=models.RoleChoice.USER,
    )
    assert not isinstance(user, Sequence)
    token = create_access_token({"user_email": user.email})
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        cookie = Cookies()
        cookie.set(config.COOKIE_NAME, token)
        ac.cookies = cookie
        yield ac


@pytest.fixture
def path_image():
    return config.ROOT_DIR / "tests" / "test-image.jpg"


@pytest.fixture(scope="package", autouse=True)
async def media_dir():
    config.MEDIA_DIR.mkdir(exist_ok=True)
    yield
    rmtree(config.MEDIA_DIR)
