from datetime import datetime, timedelta, timezone

import fastapi as fa
from fastapi.security import APIKeyCookie

from core.settings import settings


api_key = APIKeyCookie(name=settings.COOKIE_NAME, auto_error=False)


def set_cookie(response: fa.Response, token: str) -> fa.Response:
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        expires=datetime.now(timezone.utc)
        + timedelta(days=settings.COOKIE_EXPIRES),
        secure=settings.COOKIE_SECURE,
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAME_SITE,
    )
    return response


def drop_cookie(response: fa.Response) -> fa.Response:
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        secure=settings.COOKIE_SECURE,
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAME_SITE,
    )
    return response


async def get_cookie_key(token: str = fa.Security(api_key)) -> str:
    if not token:
        raise fa.HTTPException(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return token
