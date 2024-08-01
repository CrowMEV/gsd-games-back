from typing import Annotated, AsyncIterator

import jwt
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from backend import models
from backend.core.db import AsyncSession as async_project_session
from backend.core.settings import config
from backend.crud.user import get_user
from backend.schemas import user as user_schema


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with async_project_session() as session:
        yield session


AsyncSessionDepency = Annotated[
    AsyncSession, Depends(get_async_session, use_cache=True)
]


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: AsyncSessionDepency,
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        email: str = payload.get("user_email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    user = await get_user(session, email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[user_schema.User, Depends(get_current_user)],
) -> user_schema.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


GetCurrentUser = Annotated[user_schema.User, Depends(get_current_active_user)]
