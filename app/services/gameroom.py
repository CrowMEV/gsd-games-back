from typing import Any, Literal, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

import models
from repositories import GameRoomRepository
from services.service_with_image import ServiceWithImage


class GameRoomServive(ServiceWithImage[models.GameRoom]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = {
            "gameroom": GameRoomRepository(self.session),
        }

    async def get_gameroom(self, gameroom_id: int) -> models.GameRoom:
        return await self.repository["gameroom"].get_item_id(gameroom_id)

    async def get_gamerooms(self) -> Sequence[models.GameRoom]:
        return await self.repository["gameroom"].get_items()

    async def create(
        self,
        repository_name: Literal["game", "gameroom"],
        data: dict[str, Any],
    ) -> models.GameRoom:

        return await super().create(repository_name, data)

    async def update(
        self,
        repository_name: Literal["game", "gameroom"],
        data: dict[str, Any],
    ) -> models.GameRoom:

        return await super().update(repository_name, data)
