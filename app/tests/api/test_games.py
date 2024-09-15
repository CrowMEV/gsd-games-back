from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient

from tests import factory as data_factory


pytestmark = pytest.mark.anyio


async def test_get_games(
    client: AsyncClient, factory: data_factory.FactoryProtocol
):
    await factory(data_factory.GameFactory, 10)
    response = await client.get("/games/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_game_id(
    client: AsyncClient, factory: data_factory.FactoryProtocol
):
    games = await factory(data_factory.GameFactory)
    game = games.one()
    response = await client.get(f"/games/{game.id}")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert all(
        response_data[key] == getattr(game, key) for key in response_data
    )


async def test_create_game(
    admin_client: AsyncClient,
    path_image: Path,
):
    data = {
        "title": "Monopoly",
        "description": "Money money money",
        "rule_description": "mercilessly",
        "price": 500,
    }
    with open(path_image, "rb") as file:
        response = await admin_client.post(
            "/games/", data=data, files={"image": file}
        )

    assert response.status_code == status.HTTP_201_CREATED


async def test_double_title_game(
    admin_client: AsyncClient,
    path_image: Path,
):
    data = {
        "title": "Monopoly",
        "description": "Money money money",
        "rule_description": "mercilessly",
        "price": 500,
    }
    with open(path_image, "rb") as file:

        await admin_client.post("/games/", data=data, files={"image": file})
        response = await admin_client.post(
            "/games/", data=data, files={"image": file}
        )

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"Game with {data['title']} already exist"
    assert response.json()["detail"] == message


async def test_update_game(
    admin_client: AsyncClient, factory: data_factory.FactoryProtocol
):

    games = await factory(data_factory.GameFactory)
    game = games.one()

    updated_data = {"description": "Description about game 1", "price": 700}
    response = await admin_client.patch(f"/games/{game.id}", data=updated_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == updated_data["description"]
    assert response.json()["price"] == updated_data["price"]
