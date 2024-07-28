# from typing import AsyncIterator, Iterator, Type
# from urllib.parse import urlsplit

# import pytest
# from httpx import AsyncClient
# from sqlalchemy import create_engine
# from sqlalchemy.engine import Engine
# from sqlalchemy.ext.asyncio import (
#     AsyncEngine,
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
# )
# from sqlalchemy.orm import Session

# # from backend.core._typing import MODEL
# # from backend.core.dependency import get_async_session
# from backend.core.settings import config

# # from backend.main import app
# from backend.models import Base
# from utils.tests_util import tmp_database


# # from tests.factory import FACTORY, FactoryProtocol


# @pytest.fixture(scope="session", autouse=True)
# def postgres_temlate(pg_url: str) -> Iterator[str]:
#     """
#     Creates empty template database with migrations.
#     """
#     with tmp_database(pg_url, db_name="api_template") as tmp_url:
#         engine = create_engine(tmp_url)
#         Base.metadata.create_all(bind=engine)
#         engine.dispose()
#         yield tmp_url


# @pytest.fixture
# def postgres(postgres_temlate: str) -> Iterator[str]:
#     """
#     Creates empty temporary database.
#     """
#     with tmp_database(
#         postgres_temlate, suffix="api", template="api_template"
#     ) as tmp_url:
#         yield tmp_url


# @pytest.fixture
# def db(postgres_engine: Engine) -> Iterator[Session]:
#     """
#     SQLAlchemy session bound to temporary database
#     """
#     with Session(postgres_engine) as session:
#         yield session


# @pytest.fixture
# async def async_postgres_engine(postgres: str) -> AsyncIterator[AsyncEngine]:
#     """
#     SQLAlchemy async engine, bound to temporary database.
#     """
#     config.DB_NAME = urlsplit(postgres).path[1:]
#     config.DB_HOST = "localhost"
#     engine = create_async_engine(config.aync_dsn, echo=True)  # type: ignore
#     try:
#         yield engine
#     finally:
#         await engine.dispose()


# @pytest.fixture
# async def async_db(
#     async_postgres_engine: AsyncEngine,
# ) -> AsyncIterator[AsyncSession]:
#     """
#     SQLAlchemy session bound to temporary database
#     """
#     async with AsyncSession(async_postgres_engine) as session:
#         yield session


# @pytest.fixture
# async def client(async_db: AsyncSession) -> AsyncIterator[AsyncClient]:
#     """
#     TestClient for FastAPI
#     """
#     app.dependency_overrides[get_async_session] = lambda: async_db
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac
#         app.dependency_overrides = {}


# @pytest.fixture
# def factory(db: Session) -> FactoryProtocol:
#     """
#     Create factory for factory boy
#     """

#     def _factory(
#         fabric_model: Type[FACTORY], count: int, *args, **kwargs
#     ) -> list[MODEL]:
#         fabric_model._meta.sqlalchemy_session = db  # pylint: disable=W0212
#         return fabric_model.create_batch(count, *args, **kwargs)

#     return _factory
