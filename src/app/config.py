from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///:memory:"
    miner_api_base_url: AnyUrl = "http://miner:8000"
    machine_readable_checker_api_base_url: AnyUrl = "http://machine-readable-checker:8000"
    api_timeout_seconds: float = Field(default=30.0, gt=0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
