# app/core/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    QDRANT_URL: str
    QDRANT_API_KEY: str = ""
    ADMIN_API_KEY: str = "admin"
    SESSION_TTL_SECONDS: int = 3600
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> "Settings":
    return Settings()
