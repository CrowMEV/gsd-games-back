import pytest
from fastapi import status
from httpx import AsyncClient

from tests.model_factory import FactoryProtocol, UserFactory


pytestmark = pytest.mark.anyio


async def test_get_users(client: AsyncClient, factory: FactoryProtocol):

    factory(UserFactory, 10)
    response = await client.get("/users/")

    assert response.status_code == status.HTTP_200_OK


async def test_create_user(client: AsyncClient):

    data = {
        "name": "Bobik",
        "email": "e@example.com",
        "password": "password123",
    }
    response = await client.post("/users/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == data["name"]
    assert response.json()["email"] == data["email"]


async def test_update_user(client: AsyncClient, factory: FactoryProtocol):

    user = factory(UserFactory, 1)[0]

    updated_data = {"name": "updateduser", "email": "user@e.com"}
    response = await client.patch(f"/users/{user.id}", json=updated_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_data["name"]
    assert response.json()["email"] == updated_data["email"]


async def test_dublicate_email(client: AsyncClient):

    data = {
        "name": "Bobik",
        "email": "e@example.com",
        "password": "password123",
    }
    await client.post("/users/", json=data)
    response = await client.post("/users/", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"User with {data['email']} already exist"
    assert response.json()["detail"] == message


async def test_dublicate_email_update(
    client: AsyncClient, factory: FactoryProtocol
):
    user = factory(UserFactory, 1, email="e@example.com")[0]
    factory(UserFactory, 1, email="e2@ex.com")

    data = {"email": "e2@ex.com"}
    response = await client.patch(f"/users/{user.id}", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"User with {data['email']} already exist"
    assert response.json()["detail"] == message
