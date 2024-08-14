from datetime import datetime
from typing import Any, Callable, Protocol, Type, TypeVar

from factory import LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyDate, FuzzyInteger, FuzzyText

import models


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


# pylint: disable=C0301
class UserFactory(BaseFactory):
    class Meta:
        model = models.User

    password = FuzzyText()
    name = FuzzyText()
    email = LazyAttribute(lambda obj: f"{obj.name}@example.com")  # type: ignore
    avatar = ""
    birth_date = FuzzyDate(datetime(1000, 1, 1).date())
    is_active = True


# pylint: disable=C0301
class GameFactory(BaseFactory):
    class Meta:
        model = models.Game

    title = FuzzyText()
    description = FuzzyText()
    rule_description = FuzzyText()
    price = FuzzyInteger(1, 1000)
    image = FuzzyText()


FACTORY = TypeVar("FACTORY", UserFactory, GameFactory)

TypeFactory = Type[FACTORY]

UserFactoryCallback = Callable[[models.RoleChoice], dict[str, Any]]


class FactoryProtocol(Protocol):
    def __call__(
        self,
        fabric_model: Type[FACTORY],
        count: int,
        *args: Any,
        **kwargs: Any,
    ) -> list[models.MODEL]: ...
