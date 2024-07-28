from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import AsyncSession as async_project_session


async def get_async_session() -> AsyncIterator:
    async with async_project_session() as session:
        yield session


AsyncSessionDepency = Annotated[AsyncSession, Depends(get_async_session)]
