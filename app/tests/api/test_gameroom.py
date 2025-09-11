from pathlib import Path
from typing import Sequence

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests import factory as data_factory


pytestmark = pytest.mark.anyio


async def test_get_gamerooms(
    client: AsyncClient,
    factory: data_factory.FactoryCallback,
    async_session: AsyncSession,
):
    game = await factory(data_factory.GameFactory)
    office = await factory(data_factory.OfficeFactory)
    assert not isinstance(game, Sequence)
    assert not isinstance(office, Sequence)
    await async_session.refresh(game)
    await async_session.refresh(office)

    await factory(
        data_factory.GameRoomFactory, 10, game_id=game.id, office_id=office.id
    )
    response = await client.get("/gamerooms/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_gameroom_id(
    client: AsyncClient,
    factory: data_factory.FactoryCallback,
    async_session: AsyncSession,
):
    game = await factory(data_factory.GameFactory)
    office = await factory(data_factory.OfficeFactory)
    assert not isinstance(game, Sequence)
    assert not isinstance(office, Sequence)
    await async_session.refresh(game)
    await async_session.refresh(office)

    gameroom = await factory(
        data_factory.GameRoomFactory, game_id=game.id, office_id=office.id
    )
    assert not isinstance(gameroom, Sequence)
    await async_session.refresh(gameroom)

    response = await client.get(f"/gamerooms/{gameroom.id}/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_gameroom_id_not_found(
    client: AsyncClient,
):

    response = await client.get("/gamerooms/1/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "GameRoom not found"


async def test_create_gameroom(
    admin_client: AsyncClient,
    factory: data_factory.FactoryCallback,
    async_session: AsyncSession,
    path_image: Path,
):
    game = await factory(data_factory.GameFactory)
    office = await factory(data_factory.OfficeFactory)
    assert not isinstance(game, Sequence)
    assert not isinstance(office, Sequence)
    await async_session.refresh(game)
    await async_session.refresh(office)

    data = {
        "game_id": game.id,
        "office_id": office.id,
        "date": "2023-10-24",
        "price": 12500,
    }
    with open(path_image, "rb") as file:
        response = await admin_client.post(
            "/gamerooms/", data=data, files={"image": file}
        )
    assert response.status_code == status.HTTP_201_CREATED


async def test_create_gameroom_not_admin(
    user_client: AsyncClient,
    factory: data_factory.FactoryCallback,
    async_session: AsyncSession,
    path_image: Path,
):
    game = await factory(data_factory.GameFactory)
    office = await factory(data_factory.OfficeFactory)
    assert not isinstance(game, Sequence)
    assert not isinstance(office, Sequence)
    await async_session.refresh(game)
    await async_session.refresh(office)

    data = {
        "game_id": game.id,
        "office_id": office.id,
        "date": "2023-10-24",
        "price": 12500,
    }
    with open(path_image, "rb") as file:
        response = await user_client.post(
            "/gamerooms/", data=data, files={"image": file}
        )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_update_gameroom(
    admin_client: AsyncClient,
    factory: data_factory.FactoryCallback,
    async_session: AsyncSession,
):
    game = await factory(data_factory.GameFactory)
    office = await factory(data_factory.OfficeFactory)
    assert not isinstance(game, Sequence)
    assert not isinstance(office, Sequence)
    await async_session.refresh(game)
    await async_session.refresh(office)

    gameroom = await factory(
        data_factory.GameRoomFactory, game_id=game.id, office_id=office.id
    )
    assert not isinstance(gameroom, Sequence)
    await async_session.refresh(gameroom)

    updated_data = {
        "price": 38000,
    }
    response = await admin_client.patch(
        f"/gamerooms/{gameroom.id}/", data=updated_data
    )
    assert response.status_code == status.HTTP_200_OK


async def test_update_gameroom_not_found(
    admin_client: AsyncClient,
):

    updated_data = {
        "price": 38000,
    }
    response = await admin_client.patch("/gamerooms/1/", data=updated_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "GameRoom not found"


async def test_update_gameroom_not_admin(
    user_client: AsyncClient,
):

    updated_data = {
        "price": 38000,
    }
    response = await user_client.patch("/gamerooms/1/", data=updated_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
