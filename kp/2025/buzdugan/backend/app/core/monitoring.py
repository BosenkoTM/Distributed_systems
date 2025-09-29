"""
Мониторинг и метрики системы
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps
from typing import Dict, Any

# Метрики для запросов
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Метрики для приватности
PRIVACY_POLICIES_APPLIED = Counter(
    'privacy_policies_applied_total',
    'Total privacy policies applied',
    ['policy_type', 'policy_name']
)

ANONYMIZATION_OPERATIONS = Counter(
    'anonymization_operations_total',
    'Total anonymization operations',
    ['operation_type', 'table_name']
)

# Метрики для производительности
ACTIVE_CONNECTIONS = Gauge(
    'database_active_connections',
    'Number of active database connections'
)

CACHE_HIT_RATE = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)

# Метрики для безопасности
FAILED_LOGIN_ATTEMPTS = Counter(
    'failed_login_attempts_total',
    'Total failed login attempts',
    ['username', 'ip_address']
)

RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'ip_address']
)

def monitor_request(func):
    """Декоратор для мониторинга HTTP запросов"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Обновление метрик
            REQUEST_COUNT.labels(
                method=getattr(args[0], 'method', 'UNKNOWN'),
                endpoint=getattr(args[0], 'url', 'UNKNOWN'),
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=getattr(args[0], 'method', 'UNKNOWN'),
                endpoint=getattr(args[0], 'url', 'UNKNOWN')
            ).observe(duration)
    
    return wrapper

def record_privacy_policy(policy_type: str, policy_name: str):
    """Запись применения политики приватности"""
    PRIVACY_POLICIES_APPLIED.labels(
        policy_type=policy_type,
        policy_name=policy_name
    ).inc()

def record_anonymization(operation_type: str, table_name: str):
    """Запись операции анонимизации"""
    ANONYMIZATION_OPERATIONS.labels(
        operation_type=operation_type,
        table_name=table_name
    ).inc()

def record_failed_login(username: str, ip_address: str):
    """Запись неудачной попытки входа"""
    FAILED_LOGIN_ATTEMPTS.labels(
        username=username,
        ip_address=ip_address
    ).inc()

def record_rate_limit_hit(endpoint: str, ip_address: str):
    """Запись срабатывания rate limit"""
    RATE_LIMIT_HITS.labels(
        endpoint=endpoint,
        ip_address=ip_address
    ).inc()

def setup_monitoring():
    """Настройка мониторинга"""
    print("✅ Мониторинг настроен")

def get_metrics() -> str:
    """Получение метрик в формате Prometheus"""
    return generate_latest().decode('utf-8')

def get_metrics_dict() -> Dict[str, Any]:
    """Получение метрик в виде словаря"""
    return {
        "request_count": REQUEST_COUNT._value.get(),
        "request_duration": REQUEST_DURATION._sum.get(),
        "privacy_policies_applied": PRIVACY_POLICIES_APPLIED._value.get(),
        "anonymization_operations": ANONYMIZATION_OPERATIONS._value.get(),
        "active_connections": ACTIVE_CONNECTIONS._value.get(),
        "cache_hit_rate": CACHE_HIT_RATE._value.get(),
        "failed_login_attempts": FAILED_LOGIN_ATTEMPTS._value.get(),
        "rate_limit_hits": RATE_LIMIT_HITS._value.get()
    }
