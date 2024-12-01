from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    ROOT_DIR: Path = Path(__file__).parent.parent.resolve()
    MEDIA_DIR: Path = ROOT_DIR / "media"

    # run server
    DEBUG: bool = True

    # fastapi app
    APP_NAME: str = "GSD GAMES"
    APP_ALLOWED_ORIGINS: list[str] = ["*"]
    APP_ALLOWED_HOSTS: list[str] = ["*"]
    DOCS_URL: str | None = None
    REDOC_URL: str | None = None

    # JWT token
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0

    # DB settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # cookie
    COOKIE_NAME: str = "Session"
    COOKIE_SECURE: bool = False
    COOKIE_EXPIRES: int = Field(default=365, ge=1)
    COOKIE_HTTPONLY: bool = False
    COOKIE_SAME_SITE: Optional[Literal["lax", "strict", "none"]] = "lax"

    @computed_field
    def dsn(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    def async_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )


config = Config()
