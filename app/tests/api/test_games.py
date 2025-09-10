from pathlib import Path
from typing import Sequence

import pytest
from fastapi import status
from httpx import AsyncClient

from tests import factory as data_factory


pytestmark = pytest.mark.anyio


async def test_get_games(
    client: AsyncClient, factory: data_factory.FactoryCallback
):
    await factory(data_factory.GameFactory, 10)
    response = await client.get("/games/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_game_id(
    client: AsyncClient, factory: data_factory.FactoryCallback
):
    game = await factory(data_factory.GameFactory)
    assert not isinstance(game, Sequence)
    response = await client.get(f"/games/{game.id}/")
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
        "rules": "mercilessly",
        "min_people": 2,
        "max_people": 10,
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
        "rules": "mercilessly",
        "min_people": 3,
        "max_people": 11,
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
    admin_client: AsyncClient, factory: data_factory.FactoryCallback
):

    game = await factory(data_factory.GameFactory)
    assert not isinstance(game, Sequence)

    updated_data = {
        "description": "Description about game",
        "rules": "mercilessly",
    }
    response = await admin_client.patch(
        f"/games/{game.id}/", data=updated_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == updated_data["description"]
    assert response.json()["rules"] == updated_data["rules"]


async def test_update_game_with_image(
    admin_client: AsyncClient,
    path_image: Path,
):

    data = {
        "title": "Monopoly",
        "description": "Money money money",
        "rules": "mercilessly",
        "min_people": 2,
        "max_people": 10,
    }
    with open(path_image, "rb") as file:
        response = await admin_client.post(
            "/games/", data=data, files={"image": file}
        )

        assert response.status_code == status.HTTP_201_CREATED

        updated_data = {
            "description": "Description about game",
            "rules": "mercilessly",
        }
        response = await admin_client.patch(
            f"/games/{response.json()['id']}/",
            data=updated_data,
            files={"image": file},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == updated_data["description"]
    assert response.json()["rules"] == updated_data["rules"]
