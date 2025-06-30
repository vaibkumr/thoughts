import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./thoughts.db"
    TEST_DATABASE_URL: str = "sqlite:///./test_thoughts.db"
    TEST_MODE: bool = True
    MEMCACHED_HOST: str = "127.0.0.1"
    MEMCACHED_PORT: int = 11211
    GOOGLE_API_KEY: str
    APP_PASSWORD: str
    STATIC_DIR: Path = Path(__file__).parent.parent.parent / "static"
    TEMPLATES_DIR: Path = Path(__file__).parent.parent.parent / "templates"
    PROMPT_FILE: Path = Path(__file__).parent.parent.parent / "instructions.txt"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 