import datetime
from dataclasses import dataclass

import fastapi as fa
from pydantic import BaseModel, ConfigDict


class GameRoom(BaseModel):
    game_id: int
    office_id: int
    date: datetime.date
    price: int
    image: str


class GameRoomResponse(GameRoom):
    id: int
    model_config = ConfigDict(from_attributes=True)


@dataclass
class GameRoomCreate:
    game_id: int = fa.Form(...)
    office_id: int = fa.Form(...)
    price: int = fa.Form(...)
    date: datetime.date = fa.Form(...)


@dataclass
class GameRoomUpdate:
    game_id: int = fa.Form(default=None)
    office_id: int = fa.Form(default=None)
    date: datetime.date = fa.Form(default=None)
    price: int = fa.Form(default=None)
    image: str = fa.Form(default=None)
