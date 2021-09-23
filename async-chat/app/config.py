from pydantic import BaseSettings, HttpUrl, RedisDsn

MESSAGES_TO_KEEP = 50
CHANNEL_NAME = 'chan:1'


class Settings(BaseSettings):
    redis_url: RedisDsn = 'redis://localhost:6379/0'  # type: ignore
    server_url: HttpUrl = 'http://0.0.0.0:8000'  # type: ignore

    class Config:
        case_sensitive = False


settings = Settings()
