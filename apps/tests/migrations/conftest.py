from typing import Iterator

import pytest
from alembic.config import Config

from backend.core.settings import config
from utils.tests_util import make_alembic_config, tmp_database




@pytest.fixture
def postgres(pg_url: str) -> Iterator[str]:
    """
    Creates empty temporary database.
    """
    with tmp_database(pg_url, suffix="migrations") as tmp_url:
        yield tmp_url


@pytest.fixture
def alembic_config(postgres: str) -> Config:
    """
    Alembic configuration object, bound to temporary database.
    """
    return make_alembic_config(postgres, "apps")
