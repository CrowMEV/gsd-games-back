from datetime import datetime
from typing import Any, Protocol, Type

from factory import LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyDate, FuzzyText

# mypy: disable-error-code=import-untyped
from backend.core._typing import MODEL
from backend.models import User


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
    avatar = FuzzyText()
    birth_date = FuzzyDate(datetime(1000, 1, 1).date())


# pylint: disable=C0103
FACTORY_MODEL = UserFactory

TYPE_FACTORY_MODEL = Type[FACTORY_MODEL]


class FactoryProtocol(Protocol):
    def __call__(
        self,
        fabric_model: Type[FACTORY_MODEL],
        count: int,
        *args: Any,
        **kwargs: Any,
    ) -> list[MODEL]: ...
