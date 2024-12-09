from typing import Annotated

import fastapi as fa

import crud.gameroom as cgr
import models
from core import dependency
from schemas import gameroom as sgr


router = fa.APIRouter(
    prefix="/gamerooms",
    tags=["gamerooms"],
)


@router.get(
    "/",
    response_model=list[sgr.GameRoom],
)
async def get_gamerooms(session: dependency.AsyncSessionDepency):
    return await cgr.GameRoom(session).get_items()


@router.get(
    "/{gameroom_id}/",
    response_model=sgr.GameRoom,
)
async def get_gameroom_id(
    gameroom_id: int, session: dependency.AsyncSessionDepency
):
    return await cgr.GameRoom(session).get_item_id(gameroom_id)


@router.post(
    "/",
    response_model=sgr.GameRoomResponse,
    status_code=fa.status.HTTP_201_CREATED,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def create_gameroom(
    session: dependency.AsyncSessionDepency,
    image: Annotated[fa.UploadFile, fa.File()],
    gameroom_data: sgr.GameRoomCreate = fa.Depends(),
):
    data = gameroom_data.__dict__
    data["image"] = image

    result = await cgr.GameRoom(session).create_or_update("create", data)
    await session.commit()
    await session.refresh(result)
    return result


@router.patch(
    "/{gameroom_id}/",
    response_model=sgr.GameRoomResponse,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def update_gameroom(
    session: dependency.AsyncSessionDepency,
    gameroom_id: int,
    image: Annotated[fa.UploadFile, fa.File()] | None = None,
    gameroom_data: sgr.GameRoomUpdate = fa.Depends(),
):
    upload_data = {
        key: value
        for key, value in gameroom_data.__dict__.items()
        if value is not None
    }
    if image is not None:
        upload_data["image"] = image
    upload_data["id"] = gameroom_id
    result = await cgr.GameRoom(session).create_or_update(
        "update", upload_data
    )
    await session.commit()
    await session.refresh(result)
    return result
