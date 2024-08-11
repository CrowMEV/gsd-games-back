from typing import Any, Awaitable, Callable, Type

import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.game import Game


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
    result = await callback(session, model, data)

    return result
