from typing import Any, Generic, Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models


class Base(Generic[models.MODEL]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model: models.TypeModel

    async def create_item(self, data: dict[str, Any]) -> models.MODEL:
        item = await self.session.scalar(
            sa.insert(self.model).returning(self.model).values(**data)
        )
        return item  # type: ignore[return-value]

    async def get_items(self) -> Sequence[models.MODEL]:
        result = await self.session.scalars(
            sa.select(self.model).order_by(self.model.id.desc())
        )
        return result.unique().all()

    async def get_item_id(self, item_id: int) -> models.MODEL | None:
        stmt = sa.select(self.model).where(self.model.id == item_id)
        result = await self.session.scalar(stmt)
        return result

    async def update_item(self, data: dict[str, Any]) -> models.MODEL | None:
        item_id = data.pop("id")
        stmt = (
            sa.update(self.model)
            .returning(self.model)
            .where(self.model.id == item_id)
            .values(**data)
        )
        item = await self.session.scalar(stmt)
        await self.session.flush()
        return item

    async def delete_item(self, item_id: int) -> None:
        await self.session.execute(
            sa.delete(self.model).where(self.model.id == item_id)
        )
