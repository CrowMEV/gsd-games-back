from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from api import game, gameroom, office, user
from core.settings import settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings.MEDIA_DIR.mkdir(exist_ok=True)
    application.mount(
        "/media", StaticFiles(directory=settings.MEDIA_DIR), name="media"
    )

    yield


app = FastAPI(
    title=settings.APP_NAME,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan,
)


if not settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.APP_ALLOWED_ORIGINS,
        allow_credentials=True,
    )
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.APP_ALLOWED_HOSTS
    )


app.include_router(user.router)
app.include_router(game.router)
app.include_router(office.router)
app.include_router(gameroom.router)
