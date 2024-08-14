from typing import Any, Type, TypeVar

from models.base import Base
from models.game import Game
from models.user import RoleChoice, User


MODEL = TypeVar("MODEL", User, Game)

TypeModel = Type[MODEL]
