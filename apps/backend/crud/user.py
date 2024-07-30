from typing import Any, Awaitable, Callable, Type

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User


async def create_or_update_user(
    session: AsyncSession,
    model: Type[User],
    data: dict[str, Any],
    callback: Callable[
        [AsyncSession, Type[User], dict[str, Any]], Awaitable[User]
    ],
) -> User:
    try:
        result = await callback(session, model, data)
    except IntegrityError as err:
        if "ix_users_email" in err.orig.args[0]:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with {data['email']} already exist",
            ) from err
        raise err

    return result
