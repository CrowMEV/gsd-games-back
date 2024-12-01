from typing import Any, Sequence

import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import MODEL, TypeModel


class Base:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model: TypeModel

    async def create_item(self, data: dict[str, Any]) -> MODEL:
        item = await self.session.scalar(
            sa.insert(self.model).returning(self.model).values(**data)
        )
        return item  # type: ignore[return-value]

    async def get_items(self) -> Sequence[MODEL]:
        result = await self.session.scalars(
            sa.select(self.model).order_by(self.model.id.desc())
        )
        return result.unique().all()

    async def get_item_id(self, item_id: int) -> MODEL:
        stmt = sa.select(self.model).where(self.model.id == item_id)
        result = await self.session.scalar(stmt)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return result

    async def update_item(self, data: dict[str, Any]) -> MODEL:
        item_id = data.pop("id")
        stmt = (
            sa.update(self.model)
            .returning(self.model)
            .where(self.model.id == item_id)
            .values(**data)
        )
        item = await self.session.scalar(stmt)
        await self.session.flush()
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return item

    async def delete_item(self, item_id: int) -> None:
        await self.session.execute(
            sa.delete(self.model).where(self.model.id == item_id)
        )


# async def create_item(
#     session: AsyncSession, model: TypeModel, data: dict[str, Any]
# ) -> MODEL:
#     stmt = sa.insert(model).returning(model).values(**data)
#     item = await session.scalar(stmt)
#     await session.commit()
#     await session.refresh(item)
#     return item  # type: ignore


# async def get_items(
#     session: AsyncSession, model: TypeModel
# ) -> ScalarResult[MODEL]:
#     result = await session.scalars(sa.select(model))
#     return result


# async def get_item_id(
#     session: AsyncSession, model: TypeModel, item_id: int
# ) -> MODEL:
#     stmt = sa.select(model).where(model.id == item_id)
#     result = await session.scalar(stmt)
#     if result is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"{model.__name__} not found",
#         )
#     return result


# async def update_item(
#     session: AsyncSession,
#     model: TypeModel,
#     data: dict[str, Any],
# ) -> MODEL:
#     item_id = data.pop("id")
#     stmt = (
#         sa.update(model)
#         .returning(model)
#         .where(model.id == item_id)
#         .values(**data)
#     )
#     result = await session.scalar(stmt)
#     if result is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"{model.__name__} not found",
#         )
#     await session.commit()
#     await session.refresh(result)
#     return result
