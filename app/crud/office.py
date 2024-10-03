from typing import Any, Awaitable, Callable, Type

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.office import Office


cal = Callable[[AsyncSession, Type[Office], dict[str, Any]], Awaitable[Office]]


async def create_or_update_office(
    session: AsyncSession,
    model: Type[Office],
    data: dict[str, Any],
    callback: cal,
) -> Office:
    try:
        result = await callback(session, model, data)
    except IntegrityError as err:
        if (
            "address_city_constraint"
            in err.orig.args[0]  # type:ignore[union-attr]
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Office with {data['city']}, {data['address']}"
                    f" already exist"
                ),
            ) from err
        raise err

    return result
