from datetime import timedelta
from shutil import rmtree
from typing import Any, AsyncIterator, Iterator
from urllib.parse import urlsplit

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session

import models
from core.dependency import get_async_session
from core.security import create_access_token, get_password_hash
from core.settings import config
from main import app
from tests import factory_model_test
from tests.utils import tmp_database


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def postgres_temlate(pg_url: str) -> Iterator[str]:
    """
    Creates empty template database with migrations.
    """
    with tmp_database(pg_url, db_name="api_template") as tmp_url:
        engine = create_engine(tmp_url)
        models.Base.metadata.create_all(bind=engine)
        engine.dispose()
        yield tmp_url


@pytest.fixture
def postgres(postgres_temlate: str) -> Iterator[str]:
    """
    Creates empty temporary database.
    """
    with tmp_database(
        postgres_temlate, suffix="api", template="api_template"
    ) as tmp_url:
        yield tmp_url


@pytest.fixture
def db(postgres_engine: Engine) -> Iterator[Session]:
    """
    SQLAlchemy session bound to temporary database
    """
    with Session(postgres_engine) as session:
        yield session


@pytest.fixture
async def async_postgres_engine(postgres: str) -> AsyncIterator[AsyncEngine]:
    """
    SQLAlchemy async engine, bound to temporary database.
    """
    config.DB_NAME = urlsplit(postgres).path[1:]
    config.DB_HOST = "localhost"
    engine = create_async_engine(config.async_dsn, echo=True)  # type: ignore
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def async_db(
    async_postgres_engine: AsyncEngine,
) -> AsyncIterator[AsyncSession]:
    """
    SQLAlchemy session bound to temporary database
    """
    async with AsyncSession(async_postgres_engine) as session:
        yield session


@pytest.fixture
async def client(async_db: AsyncSession) -> AsyncIterator[AsyncClient]:
    """
    TestClient for FastAPI
    """
    # pylint: disable=C0301
    app.dependency_overrides[get_async_session] = lambda: async_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"  # type: ignore
    ) as ac:
        yield ac
        app.dependency_overrides = {}


@pytest.fixture
def factory(db: Session) -> factory_model_test.FactoryProtocol:
    """
    Create factory for factory boy
    """

    def _factory(
        fabric_model: factory_model_test.TypeFactory,
        count: int,
        *args,
        **kwargs
    ) -> list[models.MODEL]:
        # pylint: disable=W0212
        fabric_model._meta.sqlalchemy_session = db  # type: ignore
        return fabric_model.create_batch(count, *args, **kwargs)

    return _factory


@pytest.fixture
def user_factory(
    factory: factory_model_test.FactoryProtocol,
) -> factory_model_test.UserFactoryCallback:
    def _factory(role: models.RoleChoice) -> dict[str, Any]:

        user = factory(
            factory_model_test.UserFactory,
            1,
            password=get_password_hash("pass"),
            role=role,
        )[0]
        access_token_expires = timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        token = create_access_token(
            {"user_email": user.email}, access_token_expires
        )

        return {"user": user, "token": token}

    return _factory


@pytest.fixture
def path_image():
    return config.ROOT_DIR / "tests" / "test-image.jpg"


@pytest.fixture(scope="session", autouse=True)
def media_dir():
    config.MEDIA_DIR.mkdir(exist_ok=True)
    yield
    rmtree(config.MEDIA_DIR)
