import fastapi as fa
from fastapi.responses import JSONResponse

import models
from core import cookie, dependency, security
from schemas import status_codes as schema_status
from schemas import user as schema_user
from services import UserService


router = fa.APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/avatar/",
    response_model=schema_user.User,
    responses={
        401: {"model": schema_status.StatusCode},
    },
)
async def create_upload_avatar(
    session: dependency.AsyncSessionDepency,
    user: dependency.GetCurrentUser,
    file: fa.UploadFile,
):
    await UserService(session).set_avatar(
        user, await file.read(), str(file.filename)
    )

    await session.commit()
    await session.refresh(user)
    return user


@router.post(
    "/login/",
    response_class=JSONResponse,
    responses={401: {"model": schema_status.StatusCode}},
)
async def login(
    session: dependency.AsyncSessionDepency,
    data: schema_user.UserLogin,
):
    user = await UserService(session).login(data.model_dump())

    access_token = security.create_access_token({"user_id": user.id})
    response = JSONResponse(content="OK", status_code=fa.status.HTTP_200_OK)
    cookie.set_cookie(response, access_token)
    return response


@router.post(
    "/logout/",
    response_class=JSONResponse,
)
async def logout():
    response = JSONResponse(content="OK", status_code=fa.status.HTTP_200_OK)
    cookie.drop_cookie(response)
    return response


@router.get(
    "/",
    response_model=list[schema_user.UserResponse],
    responses={
        401: {"model": schema_status.StatusCode},
        403: {"model": schema_status.StatusCode},
    },
    dependencies=[
        fa.Depends(dependency.RoleChecker([models.RoleChoice.ADMIN]))
    ],
)
async def get_users(session: dependency.AsyncSessionDepency):
    return await UserService(session).get_users()


@router.get(
    "/me/",
    response_model=schema_user.UserResponse,
    responses={
        400: {"model": schema_status.StatusCode},
        401: {"model": schema_status.StatusCode},
    },
)
async def get_user_me(user: dependency.GetCurrentUser):
    return user


# @router.patch(
#     "/{user_id}/",
#     response_model=schema_user.UserResponse,
#     responses={

#         401: {"model": schema_status.StatusCode},
#         403: {"model": schema_status.StatusCode},
#         404: {"model": schema_status.StatusCode},
#         409: {"model": schema_status.StatusCode},
#     },
#     dependencies=[fa.Depends(dependency.get_current_active_user)],
# )
# async def update_user(
#     user_id: int,
#     user_data: schema_user.UpdateUser,
#     session: dependency.AsyncSessionDepency,
# ):
#     data = user_data.model_dump(exclude_unset=True)
#     data["id"] = user_id
#     try:
#         user = await UserService(session).update_user(data)
#     except IntegrityError as err:
#         if err.orig is not None and "ix_users_email" in err.orig.args[0]:
#             raise fa.HTTPException(
#                 status_code=fa.status.HTTP_409_CONFLICT,
#                 detail=f"User with {data['email']} already exist",
#             ) from err
#         raise err
#     if user is None:
#         raise fa.HTTPException(
#             status_code=fa.status.HTTP_404_NOT_FOUND, detail="User not found"
#         )
#     await session.commit()
#     await session.refresh(user)
#     return user
