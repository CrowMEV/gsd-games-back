from typing import Annotated, AsyncIterator

import jwt
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import models
from core import cookie, security
from core.settings import settings
from schemas import user as user_schema
from services import UserService


async def get_async_session() -> AsyncIterator[AsyncSession]:
    # pylint: disable=C0301
    async with AsyncSession(create_async_engine(settings.dsn)) as session:  # type: ignore[arg-type]
        yield session


AsyncSessionDepency = Annotated[
    AsyncSession, Depends(get_async_session, use_cache=True)
]


async def get_current_user(
    token: Annotated[str, Depends(cookie.get_cookie_key)],
    session: AsyncSessionDepency,
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("user_email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    user = await UserService(session).get_user(email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[
        user_schema.UserResponse, Depends(get_current_user)
    ],
) -> user_schema.UserResponse:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


GetCurrentUser = Annotated[
    user_schema.UserResponse, Depends(get_current_active_user)
]
AuthentificateDocs = Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]


async def secure_docs(
    credentials: AuthentificateDocs, session: AsyncSessionDepency
) -> None:
    exception_message = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )
    user = await UserService(session).get_user(credentials.username)
    if not user:
        raise exception_message
    if (
        not security.verify_password(credentials.password, user.password)
        and user.role == models.RoleChoice.ADMIN
    ):
        raise exception_message


class RoleChecker:
    def __init__(self, allowed_roles: list[models.RoleChoice]):
        self.allowed_roles = [
            models.RoleChoice(role) for role in allowed_roles
        ]

    def __call__(self, user: GetCurrentUser):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have not a permission to perform this action.",
            )
