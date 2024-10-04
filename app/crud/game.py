from pathlib import Path
from typing import Any, Awaitable, Callable, Type

import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils import write_file
from crud.common import get_item_id
from models.game import Game


async def check_duplicate_title(session: AsyncSession, title: str) -> bool:
    result = await session.execute(sa.select(Game).where(Game.title == title))
    return result.scalar() is not None


async def create_or_update_game(
    session: AsyncSession,
    model: Type[Game],
    data: dict[str, Any],
    callback: Callable[
        [AsyncSession, Type[Game], dict[str, Any]], Awaitable[Game]
    ],
) -> Game:
    if data.get("title"):
        if await check_duplicate_title(session, data["title"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Game with {data['title']} already exist",
            )
    image = data.pop("image", None)
    if image:
        game_id = data.get("id")
        if game_id:
            game = await get_item_id(session, model, game_id)
            Path(game.image).unlink()  # type:ignore[attr-defined]

        data["image"] = write_file(
            image.filename,
            await image.read(),
        )
    result = await callback(session, model, data)

    return result
