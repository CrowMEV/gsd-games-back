from pathlib import Path
from typing import Any, Generic, Literal

from sqlalchemy.ext.asyncio import AsyncSession

import models
from core.settings import settings
from services.utils import generate_file_name, remove_old_file, write_file


class ServiceWithImage(Generic[models.MODEL]):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository: dict[str, Any] = {}

    async def create(
        self,
        repository_name: Literal["game", "gameroom"],
        data: dict[str, Any],
    ) -> models.MODEL:
        image_name = data.pop("image_name")
        image_content = data.pop("image_content")
        file_name = generate_file_name(Path(image_name))
        data["image"] = f"{settings.BASE_URL}/media/{file_name}"
        item = await self.repository[repository_name].create_item(data)
        write_file(file_name, image_content)
        return item

    async def update(
        self,
        repository_name: Literal["game", "gameroom"],
        data: dict[str, Any],
    ) -> models.MODEL:
        image_name = data.pop("image_name", None)
        image_content = data.pop("image_content", None)
        file_name = ""
        old_path = ""
        if image_name is not None:
            item = await self.repository["game"].get_item_id(data["id"])
            old_path = item.image
            file_name = generate_file_name(Path(image_name))
            data["image"] = f"{settings.BASE_URL}/media/{file_name}"
        item = await self.repository[repository_name].update_item(data)
        if image_content is not None:
            remove_old_file(old_path)
            write_file(file_name, image_content)
        return item
