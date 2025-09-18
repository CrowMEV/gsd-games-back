from pathlib import Path
from typing import Sequence

import pytest
import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models
from tests import factory as data_factory


pytestmark = pytest.mark.anyio


async def test_get_users(
    admin_client: AsyncClient, factory: data_factory.FactoryCallback
):

    await factory(data_factory.UserFactory, 10)
    response = await admin_client.get("/users/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_users_user(
    user_client: AsyncClient,
    factory: data_factory.FactoryCallback,
):

    await factory(data_factory.UserFactory, 10)
    response = await user_client.get("/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_user_me(
    user_client: AsyncClient, async_session: AsyncSession
):
    users = await async_session.scalars(sa.select(models.User))
    user = users.one()
    response = await user_client.get("/users/me/")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert user.role.value == response_data["role"]
    response_data.pop("role")
    assert all(
        response_data[key] == getattr(user, key) for key in response_data
    )


# async def test_create_user(client: AsyncClient):

#     data = {
#         "name": "Bobik",
#         "email": "e@example.com",
#         "password": "password123",
#     }
#     response = await client.post("/users/", json=data)

#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.json()["name"] == data["name"]
#     assert response.json()["email"] == data["email"]


async def test_upload_avatar(
    user_client: AsyncClient,
    path_image: Path,
):
    with open(path_image, "rb") as file:
        data = {
            "file": file,
        }
        response = await user_client.post("/users/avatar/", files=data)
    assert response.status_code == status.HTTP_200_OK


async def test_login(
    client: AsyncClient,
    factory: data_factory.FactoryCallback,
):

    user = await factory(data_factory.UserFactory)
    assert not isinstance(user, Sequence)
    response = await client.post("/users/login/", json={"phone": user.phone})
    assert response.status_code == status.HTTP_200_OK
