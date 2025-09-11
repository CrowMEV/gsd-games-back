from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

import models
from repositories import OfficeRepository


class OfficeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = {
            "office": OfficeRepository(self.session),
        }

    async def get_offices(self) -> Sequence[models.Office]:
        return await self.repository["office"].get_items()

    async def get_office(self, office_id: int) -> models.Office | None:
        return await self.repository["office"].get_item_id(office_id)

    async def create_office(
        self, office_data: dict[str, Any]
    ) -> models.Office:
        return await self.repository["office"].create_item(office_data)

    async def update_office(
        self, office_data: dict[str, Any]
    ) -> models.Office | None:
        return await self.repository["office"].update_item(office_data)
