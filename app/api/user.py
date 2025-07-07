import json
from pathlib import Path

import fastapi as fa
from faker import Faker
from fastapi.responses import JSONResponse

import crud.user as cu
import models
from core import cookie, dependency, security
from core.celery_app import send_email
from core.utils import write_file
from schemas import user as schema_user


router = fa.APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/avatar/", response_model=schema_user.User)
async def create_upload_avatar(
    session: dependency.AsyncSessionDepency,
    user: dependency.GetCurrentUser,
    file: fa.UploadFile,
):
    if user.avatar != "":
        file_path = Path(user.avatar)
        file_path.unlink()

    user.avatar = write_file(
        file.filename,  # type: ignore[arg-type]
        await file.read(),
    )
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login/", response_class=JSONResponse)
async def login(
    session: dependency.AsyncSessionDepency,
    data: schema_user.UserLogin,
):
    user = await security.authenticate_user(session, **data.model_dump())
    access_token = security.create_access_token({"user_email": user.email})
    response = JSONResponse(content="OK", status_code=fa.status.HTTP_200_OK)
    cookie.set_cookie(response, access_token)
    return response


@router.post("/logout/", response_class=JSONResponse)
async def logout():
    response = JSONResponse(content="OK", status_code=fa.status.HTTP_200_OK)
    cookie.drop_cookie(response)
    return response


@router.post(
    "/",
    response_model=schema_user.UserResponse,
    status_code=fa.status.HTTP_201_CREATED,
)
async def create_user(
    user_data: schema_user.CreateUser,
    session: dependency.AsyncSessionDepency,
):
    data = user_data.model_dump()
    data["password"] = security.get_password_hash(data["password"])
    user = await cu.User(session).create_or_update("create", data)
    await session.commit()
    await session.refresh(user)
    return user


@router.get(
    "/",
    response_model=list[schema_user.UserResponse],
    dependencies=[
        fa.Depends(dependency.RoleChecker([models.RoleChoice.ADMIN]))
    ],
)
async def get_users(session: dependency.AsyncSessionDepency):
    return await cu.User(session).get_items()


@router.get("/me/", response_model=schema_user.UserResponse)
async def get_user_id(user: dependency.GetCurrentUser):
    return user


@router.patch("/", response_class=JSONResponse)
async def reset_password(
    email: schema_user.ResetPassword, session: dependency.AsyncSessionDepency
):
    user = await cu.User(session).get_user(email=email.email)
    if user is None:
        raise fa.HTTPException(
            status_code=fa.status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    password = Faker().password(length=10)
    user.password = security.get_password_hash(password)
    await session.commit()
    await session.refresh(user)
    email_data = {
        "subject": "Новый пароль от личного кабинета",
        "message": f"Новый пароль: {password}",
        "receiver_emails": [user.email],
    }
    send_email.delay(json.dumps(email_data))
    return JSONResponse(
        status_code=fa.status.HTTP_200_OK, content="Message successfully sent"
    )


@router.patch(
    "/{user_id}/",
    response_model=schema_user.UserResponse,
    dependencies=[fa.Depends(dependency.get_current_active_user)],
)
async def update_user(
    user_id: int,
    user_data: schema_user.UpdateUser,
    session: dependency.AsyncSessionDepency,
):
    data = user_data.model_dump(exclude_unset=True)
    if data.get("password"):
        data["password"] = security.get_password_hash(data["password"])
    data["id"] = user_id
    user = await cu.User(session).create_or_update("update", data)
    await session.commit()
    await session.refresh(user)
    return user
