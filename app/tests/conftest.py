from typing import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from core.settings import config


@pytest.fixture(scope="session")
def pg_url() -> str:
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    config.DB_HOST = "localhost"
    return config.dsn  # type: ignore


@pytest.fixture
def postgres_engine(
    postgres: str,
) -> Iterator[Engine]:
    """
    SQLAlchemy engine, bound to temporary database.
    """
    engine = create_engine(postgres, echo=True)
    try:
        yield engine
    finally:
        engine.dispose()
