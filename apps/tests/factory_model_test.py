from datetime import datetime
from typing import Any, Protocol, Type, TypeVar

from factory import LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyDate, FuzzyInteger, FuzzyText

from backend.core._typing import MODEL
from backend.models import Game, User


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


# pylint: disable=C0301
class UserFactory(BaseFactory):
    class Meta:
        model = User

    password = FuzzyText()
    name = FuzzyText()
    email = LazyAttribute(lambda obj: f"{obj.name}@example.com")  # type: ignore
    avatar = ""
    birth_date = FuzzyDate(datetime(1000, 1, 1).date())
    is_active = True


# pylint: disable=C0301
class GameFactory(BaseFactory):
    class Meta:
        model = Game

    title = FuzzyText()
    description = FuzzyText()
    rule_description = FuzzyText()
    price = FuzzyInteger(1, 1000)
    image = FuzzyText()


# pylint: disable=C0103
FACTORY_MODEL = TypeVar("FACTORY_MODEL", UserFactory, GameFactory)

TYPE_FACTORY_MODEL = Type[FACTORY_MODEL]


class FactoryProtocol(Protocol):
    def __call__(
        self,
        fabric_model: Type[FACTORY_MODEL],
        count: int,
        *args: Any,
        **kwargs: Any,
    ) -> list[MODEL]: ...
