from pydantic import BaseModel, ConfigDict


class Office(BaseModel):
    address: str
    city: str


class OfficeResponse(Office):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UpdateOffice(BaseModel):
    address: str | None = None
    city: str | None = None
