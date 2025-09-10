from pathlib import Path
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

import models
from core import security
from core.settings import settings
from repositories import UserRepository
from schemas import user as schema_user
from services.utils import generate_file_name, remove_old_file, write_file


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = {
            "user": UserRepository(self.session),
        }

    async def set_avatar(
        self,
        user: schema_user.UserResponse,
        file_content: bytes,
        file_name: str,
    ) -> None:
        if user.avatar != "":
            remove_old_file(user.avatar)
        avatar_name = generate_file_name(Path(file_name))
        user.avatar = f"{settings.BASE_URL}/media/{avatar_name}"
        write_file(avatar_name, file_content)

    async def get_users(self) -> Sequence[models.User]:
        return await self.repository["user"].get_items()

    async def get_user(self, email: str) -> models.User | None:
        return await self.repository["user"].get_user(email)

    async def create_user(self, user_data: dict[str, Any]) -> models.User:
        user_data["password"] = security.get_password_hash(
            user_data["password"]
        )
        return await self.repository["user"].create_item(user_data)

    async def update_user(self, user_data: dict[str, Any]) -> models.User:
        return await self.repository["user"].update_item(user_data)
