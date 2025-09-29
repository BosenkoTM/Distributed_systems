"""
Настройка подключения к базе данных
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import asyncio
from typing import Generator

from app.core.config import settings

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "development"
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Метаданные для миграций
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Инициализация базы данных"""
    try:
        # Проверка подключения
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        print("✅ База данных подключена успешно")
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        raise
