from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    database_url: str = "postgresql+asyncpg://social:social@localhost:5440/social"
    redis_url: str = "redis://localhost:6387/0"
    admin_token: str = "changeme"
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    encryption_key: str = ""
    log_level: str = "INFO"
    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()
