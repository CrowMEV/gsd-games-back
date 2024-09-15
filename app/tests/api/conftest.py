from datetime import timedelta
from shutil import rmtree
from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

import models
import tests.factory as data_factory
from core.dependency import get_async_session
from core.security import create_access_token, get_password_hash
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
    # pylint: disable=C0301

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"  # type: ignore
    ) as ac:
        yield ac


@pytest.fixture(name="factory")
async def factory_fixture(async_session: AsyncSession):
    """
    Create factory data
    """

    async def _factory(
        model_factory: data_factory.TypeFactory, *args, **kwargs
    ) -> ScalarResult[models.MODEL]:

        return await model_factory(async_session).generate_data(
            *args, **kwargs
        )

    return _factory


@pytest.fixture(name="admin_client")
async def admin_client_fixture(
    factory: data_factory.FactoryProtocol, test_app: FastAPI
):

    users = await factory(
        data_factory.UserFactory,
        password=get_password_hash("pass"),
        role=models.RoleChoice.ADMIN,
    )
    user = users.one()
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(
        {"user_email": user.email}, access_token_expires
    )
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac


@pytest.fixture(name="user_client")
async def user_client_fixture(
    factory: data_factory.FactoryProtocol, test_app: FastAPI
):

    users = await factory(
        data_factory.UserFactory,
        password=get_password_hash("pass"),
        role=models.RoleChoice.USER,
    )
    user = users.one()
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(
        {"user_email": user.email}, access_token_expires
    )
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac


@pytest.fixture
def path_image():
    return config.ROOT_DIR / "tests" / "test-image.jpg"


@pytest.fixture(scope="package", autouse=True)
async def media_dir():
    config.MEDIA_DIR.mkdir(exist_ok=True)
    yield
    rmtree(config.MEDIA_DIR)
