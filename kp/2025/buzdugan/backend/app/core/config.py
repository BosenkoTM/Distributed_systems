"""
Конфигурация приложения
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = "Privacy-Preserving Database Proxy"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "your-secret-key-here"
    
    # База данных
    DATABASE_URL: str = "postgresql://admin:secure_password_123@localhost:5432/privacy_proxy"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Безопасность
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # секунды
    
    # Приватность
    DEFAULT_K_ANONYMITY: int = 5
    DEFAULT_L_DIVERSITY: int = 3
    DEFAULT_EPSILON: float = 1.0
    DEFAULT_DELTA: float = 0.00001
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Мониторинг
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Создание экземпляра настроек
settings = Settings()
