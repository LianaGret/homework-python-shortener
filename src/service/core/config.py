from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
    DB_ECHO: bool = False

    CORS_ORIGINS: List[str] = ["*"]

    SHORT_CODE_LENGTH: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
