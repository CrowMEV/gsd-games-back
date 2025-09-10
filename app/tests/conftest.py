import pytest

from core.settings import settings


@pytest.fixture(scope="session", name="pg_url")
def pg_url_fixture() -> str:
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    settings.DB_HOST = "localhost"
    return settings.dsn  # type: ignore[return-value]
