from typing import Any, Literal

import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import crud.common as cc
import models


class User(cc.Base):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = models.User
        self.actions = {"create": self.create_item, "update": self.update_item}

    async def create_or_update(
        self, action: Literal["create", "update"], data: dict[str, Any]
    ) -> models.User:
        try:
            user: models.User = await self.actions[action](data)
        except IntegrityError as err:
            if err.orig is not None and "ix_users_email" in err.orig.args[0]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with {data['email']} already exist",
                ) from err
            raise err
        return user

    async def get_user(self, email: str) -> models.User | None:
        return await self.session.scalar(
            sa.select(self.model).where(self.model.email == email)
        )
