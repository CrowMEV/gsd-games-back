from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from api import game, gameroom, office, user
from core.dependency import secure_docs
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

    @app.get(
        "/docs",
        include_in_schema=False,
        dependencies=[Depends(secure_docs)],
    )
    async def get_swagger_documentation() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url="api/openapi.json", title="docs"
        )

    @app.get(
        "/redoc", include_in_schema=False, dependencies=[Depends(secure_docs)]
    )
    async def get_redoc_documentation():
        return get_redoc_html(openapi_url="/openapi.json", title="docs")

    @app.get(
        "/api/openapi.json",
        include_in_schema=False,
        dependencies=[Depends(secure_docs)],
    )
    async def openapi():
        return get_openapi(
            title=app.title, version=app.version, routes=app.routes
        )


app.include_router(user.router)
app.include_router(game.router)
app.include_router(office.router)
app.include_router(gameroom.router)
