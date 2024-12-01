from typing import Annotated

import fastapi as fa

import crud.game as cg
import models
from core import dependency
from schemas import game as sg


router = fa.APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[sg.Game])
async def get_games(session: dependency.AsyncSessionDepency):
    return await cg.Game(session).get_items()


@router.get("/{game_id}/", response_model=sg.Game)
async def get_game_id(game_id: int, session: dependency.AsyncSessionDepency):
    return await cg.Game(session).get_item_id(game_id)


@router.post(
    "/",
    response_model=sg.Game,
    status_code=fa.status.HTTP_201_CREATED,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def create_game(
    session: dependency.AsyncSessionDepency,
    image: Annotated[fa.UploadFile, fa.File()],
    game_data: sg.GameCreate = fa.Depends(),
):
    data = game_data.__dict__
    data["image"] = image

    game = await cg.Game(session).create_or_update("create", data)
    await session.commit()
    await session.refresh(game)
    return game


@router.patch(
    "/{game_id}/",
    response_model=sg.Game,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [models.RoleChoice.ADMIN, models.RoleChoice.STAFF]
            )
        )
    ],
)
async def update_game(
    session: dependency.AsyncSessionDepency,
    game_id: int,
    image: Annotated[fa.UploadFile, fa.File()] | None = None,
    game_data: sg.GameUpdate = fa.Depends(),
):
    upload_data = {
        key: value
        for key, value in game_data.__dict__.items()
        if value is not None
    }
    if image is not None:
        upload_data["image"] = image
    upload_data["id"] = game_id
    game = await cg.Game(session).create_or_update("update", upload_data)
    await session.commit()
    await session.refresh(game)
    return game
