#!/usr/bin/env python3
"""
Скрипт инициализации базы данных для системы разметки
"""

import asyncio
import sys
import os

# Добавление пути к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, Base, master_engine
from app.core.config import settings
from app.models import LabeledData, AnnotatorSession, VectorClock, CSVFile
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Создание таблиц в базе данных"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=master_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

async def insert_sample_data():
    """Вставка тестовых данных"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=master_engine)
        db = SessionLocal()
        
        logger.info("Inserting sample data...")
        
        # Создание тестовых CSV файлов
        sample_files = [
            {
                "filename": "sample_sentiment.csv",
                "file_path": "/app/data/sample_sentiment.csv",
                "total_rows": 1000,
                "uploaded_by": "admin"
            },
            {
                "filename": "test_dataset.csv", 
                "file_path": "/app/data/test_dataset.csv",
                "total_rows": 500,
                "uploaded_by": "admin"
            }
        ]
        
        for file_data in sample_files:
            existing_file = db.query(CSVFile).filter(
                CSVFile.filename == file_data["filename"]
            ).first()
            
            if not existing_file:
                csv_file = CSVFile(**file_data)
                db.add(csv_file)
                logger.info(f"Added sample file: {file_data['filename']}")
        
        db.commit()
        logger.info("Sample data inserted successfully")
        
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def main():
    """Основная функция инициализации"""
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Database URL: {settings.database_url}")
        
        # Создание таблиц
        await create_tables()
        
        # Вставка тестовых данных
        await insert_sample_data()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
