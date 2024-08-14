import fastapi as fa

from core import dependency
from crud import common as common_crud
from crud import game as crud_game
from models import game as model_game
from models import user as model_user
from schemas import game as schema_game


router = fa.APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=list[schema_game.Game])
async def get_games(session: dependency.AsyncSessionDepency):
    return await common_crud.get_items(session, model_game.Game)


@router.get("/{game_id}", response_model=schema_game.Game)
async def get_game_id(game_id: int, session: dependency.AsyncSessionDepency):
    return await common_crud.get_item_id(session, model_game.Game, game_id)


@router.post(
    "/",
    response_model=schema_game.Game,
    status_code=fa.status.HTTP_201_CREATED,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [model_user.RoleChoice.ADMIN, model_user.RoleChoice.STAFF]
            )
        )
    ],
)
async def create_game(
    session: dependency.AsyncSessionDepency,
    game: schema_game.GameCreate = fa.Depends(),
):
    data = game.__dict__

    result = await crud_game.create_or_update_game(
        session, model_game.Game, data, common_crud.create_item
    )
    return result


@router.patch(
    "/{game_id}",
    response_model=schema_game.Game,
    dependencies=[
        fa.Depends(
            dependency.RoleChecker(
                [model_user.RoleChoice.ADMIN, model_user.RoleChoice.STAFF]
            )
        )
    ],
)
async def update_game(
    session: dependency.AsyncSessionDepency,
    game_id: int,
    game_data: schema_game.GameUpdate = fa.Depends(),
):
    upload_data = {
        key: value
        for key, value in game_data.__dict__.items()
        if value is not None
    }

    upload_data["id"] = game_id
    result = await crud_game.create_or_update_game(
        session, model_game.Game, upload_data, common_crud.update_item
    )
    return result
