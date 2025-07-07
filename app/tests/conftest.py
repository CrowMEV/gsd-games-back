import pytest

from core.settings import config


@pytest.fixture(scope="package", name="pg_url")
def pg_url_fixture() -> str:
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    config.DB_HOST = "localhost"
    return config.dsn  # type: ignore[return-value]
