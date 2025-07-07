from pathlib import Path
from typing import Literal, Optional

from pydantic import EmailStr, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    ROOT_DIR: Path = Path(__file__).parent.parent.resolve()
    MEDIA_DIR: Path = ROOT_DIR / "media"
    BASE_URL: str = ""

    # run server
    DEBUG: bool = True

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

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

    # Email
    EMAIL_PORT: int = 465
    SMTP_SERVER: str = ""
    SENDER_EMAIL: EmailStr | None = None
    EMAIL_PASSWORD: str = ""

    @computed_field
    def dsn(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    def broker_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


config = Config()
