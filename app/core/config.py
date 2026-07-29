from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):

    # app configuration
    APP_NAME: str = "swiftlogistics core engine"
    ENVIROMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000

    DATABASE_URL: str = Field(..., description="async sqlalchemy connection string")
    TOKEN_KEY: str = Field(..., description="JWT token key")
    ALGORITHM: str = Field(..., description="jwt algorithm")
    ACCESS_TOKEN_EXPIRE: int = Field(..., description="access token expire in minute")
    REFRESH_TOKEN_EXPIRE: int = Field(..., description="refresh token expire in hour")

    # pydantic settings
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


# Using @lru_cache ensures the .env file is read from disk ONCE at startup, not on every request
@lru_cache
def get_settings() -> Settings:
    return Settings()


# Singleton instance for direct imports across your app
settings = get_settings()
