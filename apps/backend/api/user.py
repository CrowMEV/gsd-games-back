from fastapi import APIRouter, status

from backend.core.dependency import AsyncSessionDepency
from backend.crud import common as common_crud
from backend.crud import user as crud_user
from backend.models import user as model_user
from backend.schemas import user as schema_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=schema_user.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schema_user.User,
    session: AsyncSessionDepency,
):
    result = await crud_user.create_or_update_user(
        session, model_user.User, user.model_dump(), common_crud.create_item
    )
    return result


@router.get("/", response_model=list[schema_user.UserResponse])
async def get_users(session: AsyncSessionDepency):
    return await common_crud.get_items(session, model_user.User)


@router.get("/{user_id}", response_model=schema_user.UserResponse)
async def get_user_id(user_id: int, session: AsyncSessionDepency):
    return await common_crud.get_item_id(session, model_user.User, user_id)


@router.patch("/{user_id}", response_model=schema_user.UserResponse)
async def update_user(
    user_id: int, user: schema_user.UpdateUser, session: AsyncSessionDepency
):
    data = {
        key: value
        for key, value in user.model_dump().items()
        if value is not None
    }
    data["id"] = user_id
    result = await crud_user.create_or_update_user(
        session, model_user.User, data, common_crud.update_item
    )
    return result
