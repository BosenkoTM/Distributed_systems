"""
Эндпоинты для мониторинга системы
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import structlog

from app.core.database import get_db
from app.services.monitoring_service import MonitoringService
from app.services.auth_service import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/health")
async def get_health_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение статуса здоровья системы"""
    try:
        monitoring_service = MonitoringService(db)
        health_status = await monitoring_service.get_health_status()
        
        return health_status
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса здоровья: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение метрик системы"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра метрик"
            )
        
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_system_metrics()
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения метрик системы: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/performance")
async def get_performance_metrics(
    time_range: str = "1h",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение метрик производительности"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра метрик производительности"
            )
        
        monitoring_service = MonitoringService(db)
        performance_metrics = await monitoring_service.get_performance_metrics(time_range)
        
        return performance_metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения метрик производительности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/privacy-metrics")
async def get_privacy_metrics(
    time_range: str = "24h",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение метрик приватности"""
    try:
        monitoring_service = MonitoringService(db)
        privacy_metrics = await monitoring_service.get_privacy_metrics(time_range)
        
        return privacy_metrics
        
    except Exception as e:
        logger.error(f"Ошибка получения метрик приватности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/alerts")
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение активных предупреждений"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра предупреждений"
            )
        
        monitoring_service = MonitoringService(db)
        alerts = await monitoring_service.get_active_alerts()
        
        return alerts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения активных предупреждений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение данных для дашборда"""
    try:
        monitoring_service = MonitoringService(db)
        dashboard_data = await monitoring_service.get_dashboard_data(current_user)
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Ошибка получения данных дашборда: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
