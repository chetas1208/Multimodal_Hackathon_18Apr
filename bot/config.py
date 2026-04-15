from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    TELEGRAM_BOT_TOKEN: str = ""
    API_BASE_URL: str = "http://localhost:8000"
    WEBHOOK_URL: str = ""
    POLL_INTERVAL: float = 3.0
    POLL_TIMEOUT: float = 120.0


settings = Settings()
