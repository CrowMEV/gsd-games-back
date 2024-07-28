# import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


async def create_item(session: AsyncSession, model, data):
    item = model(**data)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
