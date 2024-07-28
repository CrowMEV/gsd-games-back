from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


async def create_item(session: AsyncSession, model, data: dict[str, Any]):
    item = model(**data)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_items(session: AsyncSession, model):
    return await session.scalars(sa.select(model))


async def get_item_id(session: AsyncSession, model, item_id: int):
    stmt = sa.select(model).where(model.id == item_id)
    return await session.scalar(stmt)


async def update_item(
    session: AsyncSession, model, item_id: int, data: dict[str, Any]
):
    stmt = (
        sa.update(model)
        .returning(model)
        .where(model.id == item_id)
        .values(**data)
    )
    result = await session.scalar(stmt)
    await session.commit()
    return result
