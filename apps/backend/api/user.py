from fastapi import APIRouter

from backend.core.dependency import AsyncSessionDepency
from backend.crud import common as common_crud
from backend.models import user as model_user
from backend.schemas import user as schema_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=schema_user.UserResponse)
async def create_user(user: schema_user.User, session: AsyncSessionDepency):
    result = await common_crud.create_item(
        session, model_user.User, user.model_dump()
    )

    return result
