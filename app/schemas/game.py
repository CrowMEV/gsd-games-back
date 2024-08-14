from dataclasses import dataclass

from fastapi import Form, UploadFile
from pydantic import BaseModel, ConfigDict, PositiveInt


class Game(BaseModel):
    title: str
    description: str
    rule_description: str
    price: PositiveInt
    image: str


class GameResponse(Game):
    id: int
    model_config = ConfigDict(from_attributes=True)


@dataclass
class GameCreate:
    title: str = Form(...)
    description: str = Form(...)
    rule_description: str = Form(...)
    price: PositiveInt = Form(...)
    image: UploadFile = Form(...)


@dataclass
class GameUpdate:
    title: str = Form(default=None)
    description: str = Form(default=None)
    rule_description: str = Form(default=None)
    price: PositiveInt = Form(default=None)
    image: UploadFile = Form(default=None)
