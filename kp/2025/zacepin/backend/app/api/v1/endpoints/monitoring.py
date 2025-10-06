from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from app.core.database import get_db_read, db_manager
from app.core.monitoring import metrics, session_monitor
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        # Проверка здоровья реплик
        db_manager.update_replica_health()
        
        # Получение метрик из Redis
        active_sessions = metrics.redis_client.get(f"{metrics.metrics_prefix}gauge:active_sessions") or 0
        total_requests = metrics.redis_client.get(f"{metrics.metrics_prefix}counter:total_requests") or 0
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "replicas": db_manager.replica_health,
            "active_sessions": int(active_sessions),
            "total_requests": int(total_requests)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/metrics")
async def get_metrics():
    """Получить метрики системы"""
    try:
        # Получение различных типов метрик
        counters = {}
        timings = {}
        gauges = {}
        
        # Счетчики
        counter_keys = metrics.redis_client.keys(f"{metrics.metrics_prefix}counter:*")
        for key in counter_keys:
            metric_name = key.replace(f"{metrics.metrics_prefix}counter:", "")
            counters[metric_name] = int(metrics.redis_client.get(key) or 0)
        
        # Временные метрики
        timing_keys = metrics.redis_client.keys(f"{metrics.metrics_prefix}timing:*")
        for key in timing_keys:
            metric_name = key.replace(f"{metrics.metrics_prefix}timing:", "")
            timings_raw = metrics.redis_client.lrange(key, 0, -1)
            timings[metric_name] = {
                "count": len(timings_raw),
                "avg": sum(float(t) for t in timings_raw) / len(timings_raw) if timings_raw else 0,
                "min": min(float(t) for t in timings_raw) if timings_raw else 0,
                "max": max(float(t) for t in timings_raw) if timings_raw else 0
            }
        
        # Gauge метрики
        gauge_keys = metrics.redis_client.keys(f"{metrics.metrics_prefix}gauge:*")
        for key in gauge_keys:
            metric_name = key.replace(f"{metrics.metrics_prefix}gauge:", "")
            gauges[metric_name] = float(metrics.redis_client.get(key) or 0)
        
        return {
            "counters": counters,
            "timings": timings,
            "gauges": gauges,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )

@router.get("/events")
async def get_events(
    event_type: str = None,
    limit: int = 100
):
    """Получить события системы"""
    try:
        events = []
        
        if event_type:
            # Получение событий конкретного типа
            event_keys = [f"{metrics.metrics_prefix}events:{event_type}"]
        else:
            # Получение всех событий
            event_keys = metrics.redis_client.keys(f"{metrics.metrics_prefix}events:*")
        
        for key in event_keys:
            event_type_name = key.replace(f"{metrics.metrics_prefix}events:", "")
            event_data = metrics.redis_client.lrange(key, 0, limit - 1)
            
            for event_json in event_data:
                try:
                    event = json.loads(event_json)
                    event["event_type"] = event_type_name
                    events.append(event)
                except json.JSONDecodeError:
                    continue
        
        # Сортировка по времени
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "events": events[:limit],
            "total": len(events),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events: {str(e)}"
        )

@router.get("/replicas/status")
async def get_replica_status():
    """Получить статус реплик"""
    try:
        # Обновление статуса здоровья
        db_manager.update_replica_health()
        
        replica_status = {}
        for replica_name, is_healthy in db_manager.replica_health.items():
            replica_status[replica_name] = {
                "healthy": is_healthy,
                "last_check": datetime.utcnow().isoformat()
            }
        
        return {
            "replicas": replica_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get replica status: {str(e)}"
        )

@router.get("/sessions/stats")
async def get_session_stats(
    db: Session = Depends(get_db_read)
):
    """Получить статистику сессий"""
    try:
        from app.models.annotator_session import AnnotatorSession
        
        # Общее количество сессий
        total_sessions = db.query(AnnotatorSession).count()
        active_sessions = db.query(AnnotatorSession).filter(
            AnnotatorSession.is_active == True
        ).count()
        
        # Сессии по репликам
        replica_stats = {}
        for replica in ['master', 'replica1', 'replica2']:
            count = db.query(AnnotatorSession).filter(
                AnnotatorSession.current_replica == replica,
                AnnotatorSession.is_active == True
            ).count()
            replica_stats[replica] = count
        
        # Последние активные сессии
        recent_sessions = db.query(AnnotatorSession).filter(
            AnnotatorSession.is_active == True
        ).order_by(AnnotatorSession.last_activity.desc()).limit(10).all()
        
        recent_sessions_data = []
        for session in recent_sessions:
            recent_sessions_data.append({
                "session_id": session.session_id,
                "annotator_id": session.annotator_id,
                "current_replica": session.current_replica,
                "last_activity": session.last_activity.isoformat()
            })
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "replica_distribution": replica_stats,
            "recent_sessions": recent_sessions_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session stats: {str(e)}"
        )

@router.get("/conflicts/stats")
async def get_conflict_stats(
    db: Session = Depends(get_db_read)
):
    """Получить статистику конфликтов"""
    try:
        from app.models.labeled_data import LabeledData
        
        # Общее количество конфликтов
        total_conflicts = db.query(LabeledData).filter(
            LabeledData.is_conflict == True
        ).count()
        
        # Конфликты по сессиям
        conflicts_by_session = db.query(
            LabeledData.session_id,
            db.func.count(LabeledData.id).label('conflict_count')
        ).filter(
            LabeledData.is_conflict == True
        ).group_by(LabeledData.session_id).all()
        
        # Конфликты по типам разрешения
        resolution_stats = db.query(
            LabeledData.conflict_resolution,
            db.func.count(LabeledData.id).label('count')
        ).filter(
            LabeledData.is_conflict == True
        ).group_by(LabeledData.conflict_resolution).all()
        
        return {
            "total_conflicts": total_conflicts,
            "conflicts_by_session": [
                {"session_id": item.session_id, "count": item.conflict_count}
                for item in conflicts_by_session
            ],
            "resolution_stats": [
                {"resolution": item.conflict_resolution, "count": item.count}
                for item in resolution_stats
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conflict stats: {str(e)}"
        )
