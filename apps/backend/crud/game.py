from typing import Any, Awaitable, Callable, Type

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.game import Game


async def create_or_update_game(
    session: AsyncSession,
    model: Type[Game],
    data: dict[str, Any],
    callback: Callable[
        [AsyncSession, Type[Game], dict[str, Any]], Awaitable[Game]
    ],
) -> Game:
    try:
        result = await callback(session, model, data)
    except IntegrityError as err:
        if "uq_games_title" in err.orig.args[0]:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Game with {data['title']} already exist",
            ) from err
        raise err

    return result
