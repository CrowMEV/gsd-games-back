from typing import Any, Callable, Type, TypeVar

from backend.models.game import Game
from backend.models.user import RoleChoice, User


MODEL = TypeVar("MODEL", User, Game)

TYPE_MODEL = Type[MODEL]  # pylint: disable=C0103


UserFactoryCallback = Callable[[RoleChoice], dict[str, Any]]
