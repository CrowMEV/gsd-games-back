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

    response_data = response.json()
    response_date = response_data.pop("date")
    date_object = gameroom.date.strftime("%Y-%m-%d")
    assert response_date == date_object
    assert all(
        response_data[key] == getattr(gameroom, key) for key in response_data
    )
