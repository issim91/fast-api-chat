import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Название проекта
    PROJECT_NAME: str = "Chat Application"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Настройки базы данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@db:5432/chat_db"
    )

    # Настройки безопасности
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-here"  # В продакшене обязательно заменить на реальный ключ
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]  # В продакшене заменить на конкретные домены

    class Config:
        case_sensitive = True
        env_file = ".env"

# Создаем глобальный экземпляр настроек
settings = Settings() 