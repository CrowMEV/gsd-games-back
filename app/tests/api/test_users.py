from pathlib import Path
from typing import Sequence

import pytest
import sqlalchemy as sa
from faker import Faker
from fastapi import status
from httpx import AsyncClient, Cookies
from sqlalchemy.ext.asyncio import AsyncSession

import models
from core.security import create_access_token
from core.settings import settings
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


async def test_get_user_id(
    user_client: AsyncClient, async_session: AsyncSession
):
    users = await async_session.scalars(sa.select(models.User))
    user = users.one()
    response = await user_client.get("/users/me/")
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
    user_client: AsyncClient, async_session: AsyncSession
):

    updated_data = {"name": "updateduser", "email": "user@e.com"}
    users = await async_session.scalars(sa.select(models.User))
    user = users.one()
    response = await user_client.patch(f"/users/{user.id}/", json=updated_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_data["name"]
    assert response.json()["email"] == updated_data["email"]


async def test_dublicate_email(
    client: AsyncClient, factory: data_factory.FactoryCallback, faker: Faker
):
    email = faker.email()
    await factory(data_factory.UserFactory, email=email)
    data = {
        "name": faker.name(),
        "email": email,
        "password": faker.password(),
    }
    response = await client.post("/users/", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"User with {data['email']} already exist"
    assert response.json()["detail"] == message


async def test_dublicate_email_update(
    client: AsyncClient,
    factory: data_factory.FactoryCallback,
    async_session: AsyncSession,
):

    users = await factory(data_factory.UserFactory, 2)
    user1, user2 = users
    await async_session.refresh(user1)
    await async_session.refresh(user2)
    token = create_access_token({"user_email": user1.email})
    cookie = Cookies()
    cookie.set(settings.COOKIE_NAME, token)
    client.cookies = cookie
    data = {"email": user1.email}
    response = await client.patch(
        f"/users/{user2.id}/",
        json=data,
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
    faker: Faker,
):
    password = faker.password()
    email = faker.email()
    user = await factory(
        data_factory.UserFactory, email=email, password=password
    )
    assert not isinstance(user, Sequence)
    response = await client.post(
        "/users/login/", json={"email": user.email, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK


async def test_login_with_wrong_password(
    client: AsyncClient,
    factory: data_factory.FactoryCallback,
    faker: Faker,
):
    email = faker.email()
    await factory(data_factory.UserFactory, email=email)
    response = await client.post(
        "/users/login/",
        json={"email": email, "password": faker.password()},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
