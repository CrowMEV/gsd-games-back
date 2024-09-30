from dataclasses import dataclass

from fastapi import Form, UploadFile
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
    title: str = Form(...)
    description: str = Form(...)
    rules: str = Form(...)
    image: UploadFile = Form(...)
    min_people: int = Form(...)
    max_people: int = Form(...)


@dataclass
class GameUpdate:
    title: str = Form(default=None)
    description: str = Form(default=None)
    rules: str = Form(default=None)
    image: UploadFile = Form(default=None)
    min_people: int = Form(default=None)
    max_people: int = Form(default=None)
    is_active: bool = Form(default=None)
