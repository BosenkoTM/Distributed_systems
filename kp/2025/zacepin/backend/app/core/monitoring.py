import logging
import time
from functools import wraps
from typing import Dict, Any
import json
from datetime import datetime

from app.core.database import get_redis

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Сборщик метрик для мониторинга системы"""
    
    def __init__(self):
        self.redis_client = get_redis()
        self.metrics_prefix = "labeling_system:metrics:"
    
    def increment_counter(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None):
        """Увеличить счетчик метрики"""
        try:
            key = f"{self.metrics_prefix}counter:{metric_name}"
            if tags:
                key += ":" + ":".join(f"{k}={v}" for k, v in tags.items())
            
            self.redis_client.incr(key, value)
            self.redis_client.expire(key, 86400)  # TTL 24 часа
        except Exception as e:
            logger.error(f"Failed to increment counter {metric_name}: {e}")
    
    def record_timing(self, metric_name: str, duration: float, tags: Dict[str, str] = None):
        """Записать время выполнения операции"""
        try:
            key = f"{self.metrics_prefix}timing:{metric_name}"
            if tags:
                key += ":" + ":".join(f"{k}={v}" for k, v in tags.items())
            
            # Сохраняем время выполнения
            self.redis_client.lpush(key, duration)
            self.redis_client.ltrim(key, 0, 999)  # Храним последние 1000 записей
            self.redis_client.expire(key, 86400)
        except Exception as e:
            logger.error(f"Failed to record timing {metric_name}: {e}")
    
    def set_gauge(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Установить значение метрики"""
        try:
            key = f"{self.metrics_prefix}gauge:{metric_name}"
            if tags:
                key += ":" + ":".join(f"{k}={v}" for k, v in tags.items())
            
            self.redis_client.set(key, value)
            self.redis_client.expire(key, 86400)
        except Exception as e:
            logger.error(f"Failed to set gauge {metric_name}: {e}")
    
    def record_event(self, event_name: str, data: Dict[str, Any]):
        """Записать событие"""
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": event_name,
                "data": data
            }
            
            key = f"{self.metrics_prefix}events:{event_name}"
            self.redis_client.lpush(key, json.dumps(event))
            self.redis_client.ltrim(key, 0, 999)  # Храним последние 1000 событий
            self.redis_client.expire(key, 86400)
        except Exception as e:
            logger.error(f"Failed to record event {event_name}: {e}")

# Глобальный экземпляр сборщика метрик
metrics = MetricsCollector()

def monitor_performance(metric_name: str, tags: Dict[str, str] = None):
    """Декоратор для мониторинга производительности функций"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                metrics.increment_counter(f"{metric_name}.success", tags=tags)
                return result
            except Exception as e:
                metrics.increment_counter(f"{metric_name}.error", tags=tags)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_timing(f"{metric_name}.duration", duration, tags)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                metrics.increment_counter(f"{metric_name}.success", tags=tags)
                return result
            except Exception as e:
                metrics.increment_counter(f"{metric_name}.error", tags=tags)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_timing(f"{metric_name}.duration", duration, tags)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def setup_monitoring():
    """Настройка системы мониторинга"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запись события запуска системы
    metrics.record_event("system_startup", {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "labeling-system"
    })
    
    logger.info("Monitoring system initialized")

class SessionMonitor:
    """Мониторинг сессий разметчиков"""
    
    def __init__(self):
        self.metrics = metrics
    
    def session_created(self, session_id: str, annotator_id: str, replica: str):
        """Событие создания сессии"""
        self.metrics.record_event("session_created", {
            "session_id": session_id,
            "annotator_id": annotator_id,
            "replica": replica
        })
        self.metrics.increment_counter("sessions.created", tags={"replica": replica})
    
    def session_ended(self, session_id: str, annotator_id: str, duration: float):
        """Событие завершения сессии"""
        self.metrics.record_event("session_ended", {
            "session_id": session_id,
            "annotator_id": annotator_id,
            "duration": duration
        })
        self.metrics.increment_counter("sessions.ended")
        self.metrics.record_timing("session.duration", duration)
    
    def replica_switched(self, session_id: str, from_replica: str, to_replica: str):
        """Событие переключения реплики"""
        self.metrics.record_event("replica_switched", {
            "session_id": session_id,
            "from_replica": from_replica,
            "to_replica": to_replica
        })
        self.metrics.increment_counter("replicas.switched", tags={
            "from": from_replica,
            "to": to_replica
        })
    
    def conflict_detected(self, session_id: str, conflict_type: str):
        """Событие обнаружения конфликта"""
        self.metrics.record_event("conflict_detected", {
            "session_id": session_id,
            "conflict_type": conflict_type
        })
        self.metrics.increment_counter("conflicts.detected", tags={"type": conflict_type})

# Глобальный экземпляр монитора сессий
session_monitor = SessionMonitor()
