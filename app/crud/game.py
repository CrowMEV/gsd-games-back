from pathlib import Path
from typing import Any, Literal

import sqlalchemy as sa
from fastapi import HTTPException, status

import crud.common as cc
import models
from core.utils import write_file


class Game(cc.Base):
    def __init__(self, session):
        super().__init__(session)
        self.model = models.Game
        self.actions = {"create": self.create_item, "update": self.update_item}

    async def create_or_update(
        self, action: Literal["create", "update"], data: dict[str, Any]
    ) -> models.Game:
        if data.get("title"):
            if await self.check_duplicate_title(data["title"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Game with {data['title']} already exist",
                )
        image = data.pop("image", None)
        if image:
            game_id = data.get("id")
            if game_id:
                game: models.Game = await self.get_item_id(game_id)
                Path(game.image).unlink()

            data["image"] = write_file(
                image.filename,
                await image.read(),
            )
        result = await self.actions[action](data)

        return result

    async def check_duplicate_title(self, title: str) -> bool:
        result = await self.session.execute(
            sa.select(self.model).where(self.model.title == title)
        )
        return result.scalar() is not None
