"""
Главный модуль FastAPI приложения для Privacy-Preserving прокси
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import structlog
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.api.v1.api import api_router
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.privacy_logger import PrivacyLoggerMiddleware
from app.core.monitoring import setup_monitoring

# Настройка структурированного логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при запуске
    logger.info("Запуск Privacy-Preserving прокси")
    
    # Инициализация базы данных
    await init_db()
    logger.info("База данных инициализирована")
    
    # Инициализация Redis
    await init_redis()
    logger.info("Redis инициализирован")
    
    # Настройка мониторинга
    setup_monitoring()
    logger.info("Мониторинг настроен")
    
    yield
    
    # Очистка при завершении
    logger.info("Завершение работы Privacy-Preserving прокси")

# Создание FastAPI приложения
app = FastAPI(
    title="Privacy-Preserving Database Proxy",
    description="Прокси-сервер для обеспечения приватности данных в базах данных",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавление middleware для доверенных хостов
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Добавление middleware для ограничения скорости запросов
app.add_middleware(RateLimiterMiddleware)

# Добавление middleware для логирования приватности
app.add_middleware(PrivacyLoggerMiddleware)

# Подключение маршрутов API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Privacy-Preserving Database Proxy",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Проверка подключения к базе данных
        from app.core.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Проверка подключения к Redis
        from app.core.redis_client import redis_client
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.get("/metrics")
async def metrics():
    """Эндпоинт для метрик Prometheus"""
    from app.core.monitoring import get_metrics
    return get_metrics()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
