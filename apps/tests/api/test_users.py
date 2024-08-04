from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient

from backend.core._typing import UserFactoryCallback
from backend.models.user import RoleChoice
from tests import factory_model


pytestmark = pytest.mark.anyio


async def test_get_users(
    client: AsyncClient,
    factory: factory_model.FactoryProtocol,
    user_factory: UserFactoryCallback,
):

    factory(factory_model.UserFactory, 10)
    user = user_factory(RoleChoice.ADMIN)
    headers = {"Authorization": f"Bearer {user["token"]}"}
    response = await client.get("/users/", headers=headers)
    assert response.status_code == status.HTTP_200_OK


async def test_get_users_user(
    client: AsyncClient,
    factory: factory_model.FactoryProtocol,
    user_factory: UserFactoryCallback,
):

    factory(factory_model.UserFactory, 10)
    user = user_factory(RoleChoice.USER)
    headers = {"Authorization": f"Bearer {user["token"]}"}
    response = await client.get("/users/", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_user_id(
    client: AsyncClient, user_factory: UserFactoryCallback
):

    user_dict = user_factory(RoleChoice.USER)
    user = user_dict["user"]
    response = await client.get(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {user_dict["token"]}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    response_data.pop("birth_date")
    assert user.role.value == response_data["role"]
    response_data.pop("role")
    assert all(
        response_data[key] == getattr(user, key) for key in response_data
    )
    assert "password" not in response_data


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


async def test_update_user(
    client: AsyncClient, user_factory: UserFactoryCallback
):

    user_dict = user_factory(RoleChoice.USER)
    user = user_dict["user"]
    headers = {"Authorization": f"Bearer {user_dict["token"]}"}

    updated_data = {"name": "updateduser", "email": "user@e.com"}
    response = await client.patch(
        f"/users/{user.id}", json=updated_data, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_data["name"]
    assert response.json()["email"] == updated_data["email"]


async def test_dublicate_email(
    client: AsyncClient, user_factory: UserFactoryCallback
):
    user_dict = user_factory(RoleChoice.USER)
    user = user_dict["user"]
    data = {
        "name": "Bobik",
        "email": user.email,
        "password": "password123",
    }
    response = await client.post("/users/", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"User with {data['email']} already exist"
    assert response.json()["detail"] == message


async def test_dublicate_email_update(
    client: AsyncClient, user_factory: UserFactoryCallback
):
    user = user_factory(RoleChoice.USER)["user"]
    user_dict = user_factory(RoleChoice.USER)
    user2 = user_dict["user"]
    headers = {"Authorization": f"Bearer {user_dict["token"]}"}

    data = {"email": user.email}
    response = await client.patch(
        f"/users/{user2.id}", json=data, headers=headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"User with {data['email']} already exist"
    assert response.json()["detail"] == message


async def test_invalid_password(client: AsyncClient):
    data = {
        "name": "Bobik",
        "email": "e@example.com",
        "password": "123привет",
    }
    response = await client.post("/users/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_upload_avatar(
    client: AsyncClient,
    user_factory: UserFactoryCallback,
    path_image: Path,
    delete_media_dir,
):
    user_dict = user_factory(RoleChoice.USER)
    headers = {"Authorization": f"Bearer {user_dict["token"]}"}
    with open(path_image, "rb") as file:
        data = {
            "file": file,
        }
        response = await client.post(
            "/users/avatar/", files=data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK


async def test_get_token(
    client: AsyncClient,
    user_factory: UserFactoryCallback,
):
    user_dict = user_factory(RoleChoice.USER)
    user = user_dict["user"]
    response = await client.post(
        "/users/login",
        json={"email": user.email, "password": "pass"},
    )
    assert response.status_code == status.HTTP_200_OK


async def test_get_wrong_token(
    client: AsyncClient,
    user_factory: UserFactoryCallback,
):
    user_dict = user_factory(RoleChoice.USER)
    user = user_dict["user"]
    response = await client.post(
        "/users/login",
        json={"email": user.email, "password": "parol74588"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
