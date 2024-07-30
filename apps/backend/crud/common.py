from typing import Any

import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core._typing import MODEL, TYPE_MODEL


async def create_item(
    session: AsyncSession, model: TYPE_MODEL, data: dict[str, Any]
) -> MODEL:
    stmt = sa.insert(model).returning(model).values(**data)
    item = await session.scalar(stmt)
    await session.commit()
    await session.refresh(item)
    return item  # type: ignore


async def get_items(
    session: AsyncSession, model: TYPE_MODEL
) -> ScalarResult[MODEL]:
    result = await session.scalars(sa.select(model))
    return result


async def get_item_id(
    session: AsyncSession, model: TYPE_MODEL, item_id: int
) -> MODEL:
    stmt = sa.select(model).where(model.id == item_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    return result


async def update_item(
    session: AsyncSession,
    model: TYPE_MODEL,
    data: dict[str, Any],
) -> MODEL:
    item_id = data["id"]
    stmt = (
        sa.update(model)
        .returning(model)
        .where(model.id == item_id)
        .values(**data)
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    await session.commit()
    await session.refresh(result)
    return result
