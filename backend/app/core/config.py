"""Strict configuration management for AgroPulse Copilot."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgroPulse Copilot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database (Defaults provided for local dev/testing)
    POSTGRES_USER: str = "agropulse_user"
    POSTGRES_PASSWORD: str = "agropulse_password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "agropulse_db"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI APIs
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Prevents crashes from unexpected env vars
    )

    @property
    def get_db_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

# CRITICAL: This instantiation must be at the bottom of the file
settings = Settings()
