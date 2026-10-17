from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    azure_di_endpoint: str
    azure_di_key: str
    anthropic_api_key: str
    anthropic_model: str = "claude-haiku-5-5"
    database_path: str = "resumes.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
