"""
Главный роутер API v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, privacy, query, admin, monitoring

api_router = APIRouter()

# Подключение всех эндпоинтов
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(admin.router, prefix="/admin", tags=["administration"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
