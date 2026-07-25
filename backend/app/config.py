from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = ""
    cerebras_api_key: str = ""
    gemini_api_key: str = ""

    database_url: str = "sqlite:///./data/app.db"
    qdrant_url: str = "http://localhost:6533"
    qdrant_api_key: str = ""

    cors_allowed_origins: str = "http://localhost:4200"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
