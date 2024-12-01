from typing import Any, Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import crud.common as cc
import models


class Office(cc.Base):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = models.Office
        self.actions = {"create": self.create_item, "update": self.update_item}

    async def create_or_update(
        self, action: Literal["create", "update"], data: dict[str, Any]
    ) -> models.Office:
        try:
            office: models.Office = await self.actions[action](data)
        except IntegrityError as err:
            if (
                err.orig is not None
                and "address_city_constraint" in err.orig.args[0]
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Office with {data['city']}, {data['address']}"
                        f" already exist"
                    ),
                ) from err
            raise err
        return office
