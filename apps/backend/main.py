from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.api import game, user
from backend.core.dependency import secure_docs
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
