"""
Настройка подключения к Redis
"""

import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)

# Глобальный клиент Redis
redis_client: redis.Redis = None

async def init_redis():
    """Инициализация Redis клиента"""
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Проверка подключения
        await redis_client.ping()
        logger.info("Redis подключен успешно")
        
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
        raise

async def get_redis() -> redis.Redis:
    """Получение Redis клиента"""
    if redis_client is None:
        await init_redis()
    return redis_client

async def close_redis():
    """Закрытие подключения к Redis"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
