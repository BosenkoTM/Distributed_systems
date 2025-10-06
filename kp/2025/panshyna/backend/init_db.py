#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
"""

import asyncio
import sys
import os

# Добавление пути к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция инициализации"""
    try:
        logger.info("Starting database initialization...")
        
        # Инициализация базы данных
        result = await init_database()
        logger.info(f"Database initialization result: {result}")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
