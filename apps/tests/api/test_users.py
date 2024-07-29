import pytest
from fastapi import status
from httpx import AsyncClient

from tests.model_factory import FactoryProtocol, UserFactory


pytestmark = pytest.mark.anyio


async def test_get_users(client: AsyncClient, factory: FactoryProtocol):

    factory(UserFactory, 10)
    response = await client.get("/users/")

    assert response.status_code == status.HTTP_200_OK
