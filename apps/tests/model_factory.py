from typing import Any, Protocol, Type

from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyText

from backend.core._typing import MODEL  # type: ignore
from backend.models import User  # type: ignore


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    class Meta:
        model = User

    password = FuzzyText()
    name = FuzzyText()
    email = FuzzyText()
    avatar = FuzzyText()


# pylint: disable=C0103
FACTORY_MODEL = UserFactory

TYPE_FACTORY_MODEL = Type[FACTORY_MODEL]


class FactoryProtocol(Protocol):
    def __call__(
        self,
        fabric_model: Type[FACTORY_MODEL],
        count: int,
        *args: Any,
        **kwargs: Any
    ) -> list[MODEL]: ...
