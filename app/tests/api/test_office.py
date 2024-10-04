import pytest
from fastapi import status
from httpx import AsyncClient

from tests import factory as data_factory


pytestmark = pytest.mark.anyio


async def test_get_office(
    admin_client: AsyncClient, factory: data_factory.FactoryCallback
):
    await factory(data_factory.OfficeFactory, 10)
    response = await admin_client.get("/offices/")
    assert response.status_code == status.HTTP_200_OK


async def test_get_office_id(
    admin_client: AsyncClient, factory: data_factory.FactoryCallback
):
    offices = await factory(data_factory.OfficeFactory)
    office = offices.one()
    response = await admin_client.get(f"/offices/{office.id}")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert all(
        response_data[key] == getattr(office, key) for key in response_data
    )


async def test_create_office(admin_client: AsyncClient):
    data = {
        "city": "Moscow",
        "address": "Patriky, 18",
    }
    response = await admin_client.post("/offices/", json=data)
    assert response.status_code == status.HTTP_201_CREATED


async def test_create_double_address(admin_client: AsyncClient):
    data = {
        "city": "Moscow",
        "address": "Patriky, 18",
    }
    await admin_client.post("/offices/", json=data)
    response = await admin_client.post("/offices/", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    message = f"Office with {data['city']}, {data['address']} already exist"
    assert response.json()["detail"] == message


async def test_update_office(
    admin_client: AsyncClient, factory: data_factory.FactoryCallback
):
    offices = await factory(data_factory.OfficeFactory)
    office = offices.one()

    updated_data = {
        "city": "Irkutsk",
        "address": "Lenina, 22",
    }
    response = await admin_client.patch(
        f"/offices/{office.id}", json=updated_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["city"] == updated_data["city"]
    assert response.json()["address"] == updated_data["address"]


async def test_double_update_office(
    admin_client: AsyncClient, factory: data_factory.FactoryCallback
):
    offices = await factory(data_factory.OfficeFactory)
    office = offices.one()

    updated_data = {
        "city": "Irkutsk",
        "address": "Lenina, 22",
    }
    await factory(
        data_factory.OfficeFactory,
        city=updated_data["city"],
        address=updated_data["address"],
    )
    response = await admin_client.patch(
        f"/offices/{office.id}", json=updated_data
    )
    assert response.status_code == status.HTTP_409_CONFLICT
