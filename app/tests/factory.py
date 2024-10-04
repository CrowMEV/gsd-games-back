import random
from typing import Any, Awaitable, Callable, ParamSpec, Type, TypeVar

import sqlalchemy as sa
from faker import Faker
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

import models
from core.security import get_password_hash


fake = Faker()


class DataFactory:
    def __init__(self, session: AsyncSession) -> None:
        self.list_data: list[dict[str, Any]] = []
        self.model: models.TypeModel | None = None
        self.session = session

    # pylint: disable=W0613
    async def generate_data(self, count: int, **kwargs): ...

    async def write_to_db(self) -> None:
        await self.session.execute(
            sa.insert(self.model).values(self.list_data)  # type: ignore
        )
        await self.session.commit()
        self.session.expire_all()

    async def get_data(self) -> ScalarResult[models.MODEL]:
        data = await self.session.scalars(
            sa.select(self.model)  # type:ignore[arg-type]
        )
        return data


class UserFactory(DataFactory):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = models.User

    async def generate_data(
        self, count=1, **kwargs
    ) -> ScalarResult[models.User]:
        self.list_data.extend(
            {
                "email": kwargs.get("email", fake.email()),
                "password": get_password_hash(
                    kwargs.get("password", fake.password())
                ),
                "phone": kwargs.get("phone", ""),
                "name": kwargs.get("name", fake.name()),
                "birth_date": kwargs.get("birth_date", fake.date_of_birth()),
                "is_active": kwargs.get("is_active", True),
                "role": kwargs.get(
                    "role", random.choice(list(models.RoleChoice))
                ),
            }
            for _ in range(count)
        )
        await self.write_to_db()
        return await self.get_data()


class GameFactory(DataFactory):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = models.Game

    async def generate_data(
        self, count=1, **kwargs
    ) -> ScalarResult[models.User]:
        self.list_data.extend(
            {
                "title": kwargs.get("title", fake.word()),
                "description": kwargs.get("description", fake.text()),
                "rules": kwargs.get("rules", fake.text()),
                "image": kwargs.get("image", "media/test-image.jpg"),
                "min_people": kwargs.get("min_people", fake.pyint()),
                "max_people": kwargs.get("max_people", fake.pyint()),
                "is_active": kwargs.get("is_active", fake.pybool()),
            }
            for _ in range(count)
        )
        await self.write_to_db()
        return await self.get_data()


class OfficeFactory(DataFactory):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = models.Office

    async def generate_data(
        self, count=1, **kwargs
    ) -> ScalarResult[models.Office]:
        self.list_data.extend(
            {
                "city": kwargs.get("city", fake.city()),
                "address": kwargs.get("address", fake.address()),
            }
            for _ in range(count)
        )
        await self.write_to_db()
        return await self.get_data()


P = ParamSpec("P")
FACTORY = TypeVar("FACTORY", bound=DataFactory)


TypeFactory = Type[FACTORY]
FactoryCallback = Callable[P, Awaitable[ScalarResult[models.MODEL]]]
