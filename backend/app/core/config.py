from pathlib import Path
from typing import List

from pydantic import BaseSettings, PostgresDsn, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    DISCORD_CLIENT_ID: str | None = None
    DISCORD_CLIENT_SECRET: str | None = None
    DISCORD_REDIRECT_URI: str | None = None
    BACKEND_CORS_ORIGINS: List[str] = ['*']
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = BASE_DIR.parent.parent / '.env'
        env_file_encoding = 'utf-8'

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',') if origin.strip()]
        return value

settings = Settings()
