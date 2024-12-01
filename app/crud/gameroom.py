from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import sqlalchemy as sa

import crud.common as cc
import models
from core.utils import write_file


class GameRoom(cc.Base):
    def __init__(self, session):
        super().__init__(session)
        self.model = models.GameRoom
        self.actions = {"create": self.create_item, "update": self.update_item}

    async def check_date_game(self, date: datetime) -> bool:
        result = await self.session.execute(
            sa.select(self.model).where(self.model.date == date)
        )
        return result.scalar() is not None

    async def create_or_update(
        self,
        action: Literal["create", "update"],
        data: dict[str, Any],
    ) -> models.GameRoom:
        image = data.pop("image", None)
        if image:
            gameroom_id = data.get("id")
            if gameroom_id:
                gameroom: models.GameRoom = await self.get_item_id(gameroom_id)
                Path(gameroom.image).unlink()

            data["image"] = write_file(
                image.filename,
                await image.read(),
            )

        result = await self.actions[action](data)
        return result
