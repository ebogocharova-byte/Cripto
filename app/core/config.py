from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://trading:trading@localhost:5432/trading"
    n8n_webhook_secret: str | None = None
    binance_api_base: str = "https://api.binance.com"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
