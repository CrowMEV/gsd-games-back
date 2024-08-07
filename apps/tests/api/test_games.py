import pytest
from fastapi import status
from httpx import AsyncClient

from backend.core._typing import UserFactoryCallback
from backend.models.user import RoleChoice
from tests import factory_model


pytestmark = pytest.mark.anyio


async def test_get_games(
    client: AsyncClient,
    factory: factory_model.FactoryProtocol,
):
    factory(factory_model.GameFactory, 10)
    response = await client.get("/games/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_game_id(
    client: AsyncClient,
    factory: factory_model.FactoryProtocol,
):
    game = factory(factory_model.GameFactory, 1)[0]
    response = await client.get(f"/games/{game.id}")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert all(
        response_data[key] == getattr(game, key) for key in response_data
    )


async def test_create_game(
    client: AsyncClient, user_factory: UserFactoryCallback
):
    user_dict = user_factory(RoleChoice.ADMIN)
    headers = {"Authorization": f"Bearer {user_dict["token"]}"}
    data = {
        "title": "Monopoly",
        "description": "Money money money",
        "rule_description": "mercilessly",
        "price": 500,
    }
    response = await client.post("/games/", json=data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED


async def test_double_title_game(
    client: AsyncClient, user_factory: UserFactoryCallback
):
    user_dict = user_factory(RoleChoice.ADMIN)
    headers = {"Authorization": f"Bearer {user_dict["token"]}"}
    data = {
        "title": "Monopoly",
        "description": "Money money money",
        "rule_description": "mercilessly",
        "price": 500,
    }
    await client.post("/games/", json=data, headers=headers)
    response = await client.post("/games/", json=data, headers=headers)

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"Game with {data['title']} already exist"
    assert response.json()["detail"] == message


async def test_update_game(
    client: AsyncClient,
    user_factory: UserFactoryCallback,
    factory: factory_model.FactoryProtocol,
):
    user_dict = user_factory(RoleChoice.ADMIN)
    headers = {"Authorization": f"Bearer {user_dict["token"]}"}

    game = factory(factory_model.GameFactory, 1)[0]

    updated_data = {"description": "Description about game 1", "price": 700}
    response = await client.patch(
        f"/games/{game.id}", json=updated_data, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == updated_data["description"]
    assert response.json()["price"] == updated_data["price"]
