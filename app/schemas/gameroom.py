import datetime

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


class GameRoomUpdate(BaseModel):
    game_id: int | None = None
    office_id: int | None = None
    date: datetime.date | None = None
    price: int | None = None
    image: str | None = None
