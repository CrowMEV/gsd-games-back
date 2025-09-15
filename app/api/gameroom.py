from typing import Annotated

import fastapi as fa

import models
from core import dependency
from schemas import gameroom as schema_gamerooms
from services import GameRoomServive


router = fa.APIRouter(
    prefix="/gamerooms",
    tags=["gamerooms"],
)


@router.get(
    "/",
    response_model=list[schema_gamerooms.GameRoomResponse],
    responses={200: {"description": "Ok"}},
)
async def get_gamerooms(session: dependency.AsyncSessionDepency):
    return await GameRoomServive(session).get_gamerooms()


@router.get(
    "/{gameroom_id}/",
    response_model=schema_gamerooms.GameRoomResponse,
    responses={200: {"description": "Ok"}, 404: {"description": "Not found"}},
)
async def get_gameroom_id(
    gameroom_id: int, session: dependency.AsyncSessionDepency
):
    gameroom = await GameRoomServive(session).get_gameroom(gameroom_id)
    if gameroom is None:
        raise fa.HTTPException(
            status_code=fa.status.HTTP_404_NOT_FOUND,
            detail="GameRoom not found",
        )
    return gameroom


@router.post(
    "/",
    response_model=schema_gamerooms.GameRoomResponse,
    status_code=fa.status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        409: {"description": "Conflict"},
    },
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
    gameroom_data: schema_gamerooms.GameRoomCreate = fa.Depends(),
):
    data = gameroom_data.__dict__
    data["image_name"] = image.filename
    data["image_content"] = await image.read()
    gameroom = await GameRoomServive(session).create("gameroom", data)
    await session.commit()
    await session.refresh(gameroom)
    return gameroom


@router.patch(
    "/{gameroom_id}/",
    response_model=schema_gamerooms.GameRoomResponse,
    responses={
        200: {"description": "Created"},
        404: {"description": "Not found"},
        409: {"description": "Conflict"},
    },
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
    image: fa.UploadFile | None = None,
    gameroom_data: schema_gamerooms.GameRoomUpdate = fa.Depends(),
):
    data = {
        key: value
        for key, value in gameroom_data.__dict__.items()
        if value is not None
    }
    if image is not None:
        data["image_name"] = image.filename
        data["image_content"] = await image.read()
    data["id"] = gameroom_id
    gameroom = await GameRoomServive(session).update("gameroom", data)
    if gameroom is None:
        raise fa.HTTPException(
            status_code=fa.status.HTTP_404_NOT_FOUND,
            detail="GameRoom not found",
        )
    await session.commit()
    await session.refresh(gameroom)
    return gameroom
