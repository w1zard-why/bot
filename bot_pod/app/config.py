# bot/app/config.py
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings          # <-- новая
from pydantic import Field, PostgresDsn             # остальное без изменений


class Settings(BaseSettings):
    BOT_TOKEN: str
    PG_DSN: PostgresDsn
    GIFT_API_BASE: str = "https://gift.example.com"
    PAYMENT_PROVIDER_TOKEN: str | None = None
    ADMINS: str = ""
    TG_MODE: Literal["webhook", "polling"] = "polling"
    WEBHOOK_BASE: str | None = None

    INITIAL_STARS: int = 5
    AUTOBUY_INTERVAL: int = 15  # minutes

    RATE_LIMIT_CMDS: int = 5
    RATE_LIMIT_WINDOW: int = 10  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:  # noqa: D401
    """Return cached settings instance."""
    return Settings()
