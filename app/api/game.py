from typing import Annotated

import fastapi as fa
from sqlalchemy.exc import IntegrityError

import models
from core import dependency
from schemas import game as schema_game
from services import GameService


router = fa.APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[schema_game.GameResponse])
async def get_games(session: dependency.AsyncSessionDepency):
    return await GameService(session).get_games()


@router.get("/{game_id}/", response_model=schema_game.GameResponse)
async def get_game_id(game_id: int, session: dependency.AsyncSessionDepency):
    game = await GameService(session).get_game(game_id)
    if game is None:
        raise fa.HTTPException(
            status_code=fa.status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


@router.post(
    "/",
    response_model=schema_game.GameResponse,
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
    game_data: schema_game.GameCreate = fa.Depends(),
):
    data = game_data.__dict__
    data["image_name"] = image.filename
    data["image_content"] = await image.read()
    try:
        game = await GameService(session).create("game", data)
    except IntegrityError as err:
        if err.orig is not None and "uq_games_title" in err.orig.args[0]:
            raise fa.HTTPException(
                status_code=fa.status.HTTP_409_CONFLICT,
                detail=f"Game with {data['title']} already exist",
            ) from err
        raise err
    await session.commit()
    await session.refresh(game)
    return game


@router.patch(
    "/{game_id}/",
    response_model=schema_game.GameResponse,
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
    image: fa.UploadFile | None = None,
    game_data: schema_game.GameUpdate = fa.Depends(),
):
    data = {
        key: value
        for key, value in game_data.__dict__.items()
        if value is not None
    }
    if image is not None:
        data["image_name"] = image.filename
        data["image_content"] = await image.read()
    data["id"] = game_id
    try:
        game = await GameService(session).update("game", data)
    except IntegrityError as err:
        if err.orig is not None and "uq_games_title" in err.orig.args[0]:
            raise fa.HTTPException(
                status_code=fa.status.HTTP_409_CONFLICT,
                detail=f"Game with {data['title']} already exist",
            ) from err
        raise err
    if game is None:
        raise fa.HTTPException(
            status_code=fa.status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    await session.commit()
    await session.refresh(game)
    return game
