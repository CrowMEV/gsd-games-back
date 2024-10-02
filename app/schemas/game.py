from dataclasses import dataclass

import fastapi as fa
from pydantic import BaseModel, ConfigDict


class Game(BaseModel):
    title: str
    description: str
    rules: str
    image: str
    min_people: int
    max_people: int


class GameResponse(Game):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


@dataclass
class GameCreate:
    title: str = fa.Form(...)
    description: str = fa.Form(...)
    rules: str = fa.Form(...)
    min_people: int = fa.Form(...)
    max_people: int = fa.Form(...)


@dataclass
class GameUpdate:
    title: str = fa.Form(default=None)
    description: str = fa.Form(default=None)
    rules: str = fa.Form(default=None)
    min_people: int = fa.Form(default=None)
    max_people: int = fa.Form(default=None)
    is_active: bool = fa.Form(default=None)
