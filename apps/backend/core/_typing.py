from typing import Any, Callable, Type

from backend.models.user import RoleChoice, User


MODEL = User

TYPE_MODEL = Type[MODEL]  # pylint: disable=C0103


UserFactoryCallback = Callable[[RoleChoice], dict[str, Any]]
