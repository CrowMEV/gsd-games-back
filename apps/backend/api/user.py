from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, status

from backend.core import security
from backend.core.dependency import AsyncSessionDepency, GetCurrentUser
from backend.core.settings import config
from backend.crud import common as common_crud
from backend.crud import user as crud_user
from backend.models import user as model_user
from backend.schemas import user as schema_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/avatar/", response_model=schema_user.User)
async def create_upload_avatar(
    session: AsyncSessionDepency, user: GetCurrentUser, file: UploadFile
):
    db_user = await crud_user.get_user(session, user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if db_user.avatar != "":
        file_path = Path(db_user.avatar)
        file_path.unlink()
    avatar_name = Path(file.filename)  # type: ignore

    path_avatar = (
        config.MEDIA_DIR
        / f"{avatar_name.stem}{str(uuid4())}{avatar_name.suffix}"
    )
    path_avatar.write_bytes(await file.read())
    db_user.avatar = str(path_avatar)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/login", response_model=schema_user.Token)
async def login_for_access_token(
    session: AsyncSessionDepency,
    data: schema_user.UserLogin,
):
    user = await security.authenticate_user(session, **data.model_dump())
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        {"user_email": user.email}, access_token_expires
    )
    return schema_user.Token(token=access_token)


@router.post(
    "/",
    response_model=schema_user.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schema_user.CreateUser,
    session: AsyncSessionDepency,
):
    data = user.model_dump()
    data["password"] = security.get_password_hash(data["password"])
    result = await crud_user.create_or_update_user(
        session, model_user.User, data, common_crud.create_item
    )
    return result


@router.get("/", response_model=list[schema_user.UserResponse])
async def get_users(session: AsyncSessionDepency):
    return await common_crud.get_items(session, model_user.User)


@router.get("/{user_id}", response_model=schema_user.UserResponse)
async def get_user_id(user: GetCurrentUser):
    return user


@router.patch("/{user_id}", response_model=schema_user.UserResponse)
async def update_user(
    user_id: int, user: schema_user.UpdateUser, session: AsyncSessionDepency
):
    data = {
        key: value
        for key, value in user.model_dump().items()
        if value is not None
    }
    if data.get("password"):
        data["password"] = security.get_password_hash(data["password"])
    data["id"] = user_id
    result = await crud_user.create_or_update_user(
        session, model_user.User, data, common_crud.update_item
    )
    return result
