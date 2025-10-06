from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
from typing import Generator, Dict, Any
import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Создание базового класса для моделей
Base = declarative_base()

# Создание движков для разных реплик
master_engine = create_engine(
    settings.master_db_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug
)

replica1_engine = create_engine(
    settings.replica1_db_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.debug
)

replica2_engine = create_engine(
    settings.replica2_db_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.debug
)

# Создание сессий
MasterSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=master_engine)
Replica1SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=replica1_engine)
Replica2SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=replica2_engine)

# Redis клиент
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

class DatabaseManager:
    """Менеджер для работы с множественными репликами БД"""
    
    def __init__(self):
        self.replicas = {
            'master': MasterSessionLocal,
            'replica1': Replica1SessionLocal,
            'replica2': Replica2SessionLocal
        }
        self.current_replica = 'master'
        self.replica_health = {
            'master': True,
            'replica1': True,
            'replica2': True
        }
    
    def get_write_session(self) -> Session:
        """Получить сессию для записи (только master)"""
        return self.replicas['master']()
    
    def get_read_session(self, replica: str = None) -> Session:
        """Получить сессию для чтения с балансировкой нагрузки"""
        if replica and replica in self.replicas:
            return self.replicas[replica]()
        
        # Выбор здоровой реплики для чтения
        healthy_replicas = [r for r, healthy in self.replica_health.items() if healthy]
        if not healthy_replicas:
            # Если все реплики недоступны, используем master
            return self.replicas['master']()
        
        # Простая round-robin балансировка
        selected_replica = healthy_replicas[self.current_replica_index % len(healthy_replicas)]
        self.current_replica_index = (self.current_replica_index + 1) % len(healthy_replicas)
        
        return self.replicas[selected_replica]()
    
    def check_replica_health(self, replica: str) -> bool:
        """Проверить здоровье реплики"""
        try:
            session = self.replicas[replica]()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Replica {replica} health check failed: {e}")
            return False
    
    def update_replica_health(self):
        """Обновить статус здоровья всех реплик"""
        for replica in self.replicas.keys():
            self.replica_health[replica] = self.check_replica_health(replica)

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()

# Зависимости для FastAPI
def get_db_write() -> Generator[Session, None, None]:
    """Зависимость для получения сессии записи"""
    db = db_manager.get_write_session()
    try:
        yield db
    finally:
        db.close()

def get_db_read(replica: str = None) -> Generator[Session, None, None]:
    """Зависимость для получения сессии чтения"""
    db = db_manager.get_read_session(replica)
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Инициализация базы данных"""
    try:
        # Создание таблиц
        Base.metadata.create_all(bind=master_engine)
        logger.info("Database initialized successfully")
        
        # Проверка здоровья реплик
        db_manager.update_replica_health()
        logger.info(f"Replica health status: {db_manager.replica_health}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Функция для получения Redis клиента
def get_redis() -> redis.Redis:
    return redis_client
