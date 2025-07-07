from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    PG_DSN: str
    TG_MODE: str = "polling"
    GIFT_API_BASE: str
    PAYMENT_PROVIDER_TOKEN: str = ""
    INITIAL_STARS: int = 0
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_CMDS: int = 5

    TG_API_ID: int
    TG_API_HASH: str
    TG_PHONE: str
    TG_SESSION: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

def get_settings() -> Settings:
    return Settings()
