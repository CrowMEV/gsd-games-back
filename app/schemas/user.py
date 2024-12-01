import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.functional_validators import AfterValidator

from models.user import RoleChoice


def check_password(password: str) -> str:
    assert len(password) >= 8, "Password is sholter than 8 characters"
    assert not re.search(
        r"[а-яА-Я]", password
    ), "Password must contain only English letters"
    return password


Password = Annotated[str, AfterValidator(check_password)]


class Token(BaseModel):
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr
    name: str
    avatar: str = ""
    phone: str = ""
    birth_date: datetime | None = None
    is_active: bool = True


class CreateUser(User):
    password: Password
    phone: str = ""


class UserResponse(User):
    id: int
    role: RoleChoice
    phone: str
    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    birth_date: datetime | None = None
    phone: str | None = None
