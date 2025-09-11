from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

import models
from repositories import GameRepository
from services.service_with_image import ServiceWithImage


class GameService(ServiceWithImage[models.Game]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = {
            "game": GameRepository(self.session),
        }

    async def get_game(self, game_id: int) -> models.Game | None:
        return await self.repository["game"].get_item_id(game_id)

    async def get_games(self) -> Sequence[models.Game]:
        return await self.repository["game"].get_items()
