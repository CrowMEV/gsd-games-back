import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import AfterValidator

from models.user import RoleChoice


def check_phone(phone: str) -> str:

    assert re.search(
        r"^\+7\d{10}$", phone
    ), "Телефон должен быть в формате +7XXXXXXXXXX"
    return phone


Phone = Annotated[str, AfterValidator(check_phone)]


class Token(BaseModel):
    token: str


class UserLogin(BaseModel):
    phone: Phone


class User(BaseModel):
    name: str
    avatar: str = ""
    phone: Phone
    is_active: bool = True


class UserResponse(User):
    id: int
    role: RoleChoice
    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseModel):
    name: str | None = None
    phone: Phone | None = None
