from pydantic import BaseModel, ConfigDict, PositiveInt


class Game(BaseModel):
    title: str
    description: str
    rule_description: str
    price: PositiveInt


class GameResponse(Game):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    rule_description: str | None = None
    price: PositiveInt | None = None
