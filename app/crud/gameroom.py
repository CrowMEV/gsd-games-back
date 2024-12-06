from datetime import datetime

import sqlalchemy as sa

import crud.common as cc
import models


class GameRoom(cc.Base, cc.MixinImage):
    def __init__(self, session):
        super().__init__(session)
        self.model = models.GameRoom
        self.actions = {"create": self.create_item, "update": self.update_item}

    async def check_date_game(self, date: datetime) -> bool:
        result = await self.session.execute(
            sa.select(self.model).where(self.model.date == date)
        )
        return result.scalar() is not None
