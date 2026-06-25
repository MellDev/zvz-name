from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except Exception:
    from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str = 'sqlite+pysqlite:///:memory:'
    SECRET_KEY: str = 'test-secret'
    DISCORD_CLIENT_ID: str | None = None
    DISCORD_CLIENT_SECRET: str | None = None
    DISCORD_REDIRECT_URI: str | None = None
    DISCORD_SCOPES: str = 'identify'
    DISCORD_DEFAULT_GUILD_ID: int = 1
    DISCORD_WEBHOOK_URL: str | None = None
    DISCORD_BOT_TOKEN: str | None = None
    DISCORD_ANNOUNCEMENT_CHANNEL_ID: str | None = None
    FRONTEND_URL: str = 'http://localhost:3000'
    BACKEND_CORS_ORIGINS: str = '*'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    class Config:
        env_file = BASE_DIR.parent.parent / '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'

    @property
    def cors_origins(self) -> list[str]:
        if self.BACKEND_CORS_ORIGINS.strip() == '*':
            return ['*']
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(',') if origin.strip()]

settings = Settings()
