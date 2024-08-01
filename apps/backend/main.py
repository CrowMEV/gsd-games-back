from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import user
from backend.core.settings import config


app = FastAPI(
    title=config.APP_NAME,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
)
app.mount("/media", StaticFiles(directory=config.MEDIA_DIR), name="media")

if not config.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.APP_ALLOWED_ORIGINS,
        allow_credentials=True,
    )
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=config.APP_ALLOWED_HOSTS
    )


app.include_router(user.router)
