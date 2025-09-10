from datetime import datetime

import sqlalchemy as sa

import models
import repositories.common as common_repository


class GameRoom(common_repository.Base[models.GameRoom]):
    def __init__(self, session):
        super().__init__(session)
        self.model = models.GameRoom

    async def check_date_game(self, date: datetime) -> bool:
        result = await self.session.execute(
            sa.select(self.model).where(self.model.date == date)
        )
        return result.scalar() is not None
