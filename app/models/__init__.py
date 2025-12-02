from typing import Type, TypeVar

from models.base import Base
from models.game import Game
from models.gameroom import GameRoom
from models.office import Office
from models.user import RoleChoice, User


MODEL = TypeVar("MODEL", bound=Base)

TypeModel = Type[MODEL]
