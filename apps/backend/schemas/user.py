from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    email: EmailStr
    password: str
    name: str
    avatar: str = ""
    birth_date: datetime | None = None


class UserResponse(User):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    avatar: str | None = None
    birth_date: datetime | None = None
