from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://postgres:postgres@postgres-master:5432/labeling_db"
    master_db_url: str = "postgresql://postgres:postgres@postgres-master:5432/labeling_db"
    replica1_db_url: str = "postgresql://postgres:postgres@postgres-replica-1:5432/labeling_db"
    replica2_db_url: str = "postgresql://postgres:postgres@postgres-replica-2:5432/labeling_db"
    
    # Redis settings
    redis_url: str = "redis://redis:6379"
    
    # Application settings
    app_name: str = "Labeling System"
    debug: bool = True
    secret_key: str = "your-secret-key-here"
    
    # Vector clock settings
    max_clock_size: int = 1000
    clock_cleanup_interval: int = 3600  # seconds
    
    # Session settings
    session_timeout: int = 3600  # seconds
    max_concurrent_sessions: int = 100
    
    # File upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: List[str] = [".csv", ".txt"]
    upload_dir: str = "/app/data"
    
    # Replica settings
    replica_read_timeout: float = 5.0
    replica_health_check_interval: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()
