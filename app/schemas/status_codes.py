from pydantic import BaseModel


class StatusCode(BaseModel):
    detail: str
