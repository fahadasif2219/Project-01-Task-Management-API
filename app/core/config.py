"""Application configuration."""

import sys
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    DATABASE_URL: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    try:
        return Settings()
    except Exception as e:
        print(f"\n[ERROR] Configuration failed: {e}")
        print("\nMake sure you have a .env file with DATABASE_URL set.")
        print("Example: DATABASE_URL='postgresql+asyncpg://user:pass@host/db?sslmode=require'")
        sys.exit(1)
