from pathlib import Path
from typing import Any, Literal, Protocol, Sequence

import fastapi as fa
import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import models
from core.utils import write_file
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


class BaseCRUDprotocol(Protocol):
    async def create_item(self, data: dict[str, Any]) -> models.MODEL: ...
    async def get_items(self) -> Sequence[models.MODEL]: ...
    async def get_item_id(self, item_id: int) -> models.MODEL: ...
    async def update_item(self, data: dict[str, Any]) -> models.MODEL: ...
    async def delete_item(self, item_id: int) -> None: ...
    async def create_image(
        self,
        image: fa.UploadFile,
        item_id: int | None = None,
    ): ...


class MixinImage:
    async def create_image(
        self,
        image: fa.UploadFile,
        item_id: int | None = None,
    ) -> str:
        if item_id is not None:
            item: models.MODEL_IMAGE = (
                await self.get_item_id(  # type:ignore[attr-defined]
                    item_id
                )
            )
            Path(item.image).unlink()

        return write_file(
            image.filename,  # type: ignore[arg-type]
            await image.read(),
        )

    async def create_or_update(
        self,
        action: Literal["create", "update"],
        data: dict[str, Any],
    ) -> models.MODEL_IMAGE:
        image = data.pop("image", None)
        if image:
            data["image"] = await self.create_image(image, data.get("id"))

        result = await self.actions[action](data)  # type:ignore[attr-defined]
        return result
