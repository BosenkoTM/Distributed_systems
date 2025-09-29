"""
Middleware для ограничения скорости запросов
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import asyncio
from typing import Dict, Tuple
import structlog

from app.core.redis_client import get_redis
from app.core.config import settings
from app.core.monitoring import record_rate_limit_hit

logger = structlog.get_logger(__name__)

class RateLimiterMiddleware:
    """Middleware для ограничения скорости запросов"""
    
    def __init__(self, app):
        self.app = app
        self.redis_client = None
        self.rate_limit_requests = settings.RATE_LIMIT_REQUESTS
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Получение IP адреса клиента
        client_ip = self.get_client_ip(request)
        
        # Проверка rate limit
        if await self.is_rate_limited(client_ip, request.url.path):
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                endpoint=request.url.path
            )
            
            # Запись метрики
            record_rate_limit_hit(request.url.path, client_ip)
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self.rate_limit_window
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    def get_client_ip(self, request: Request) -> str:
        """Получение IP адреса клиента"""
        # Проверка заголовков прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Возврат IP из соединения
        return request.client.host if request.client else "unknown"
    
    async def is_rate_limited(self, client_ip: str, endpoint: str) -> bool:
        """Проверка превышения лимита запросов"""
        try:
            redis_client = await get_redis()
            
            # Создание ключа для rate limiting
            key = f"rate_limit:{client_ip}:{endpoint}"
            current_time = int(time.time())
            window_start = current_time - self.rate_limit_window
            
            # Удаление старых записей
            await redis_client.zremrangebyscore(key, 0, window_start)
            
            # Подсчет текущих запросов
            current_requests = await redis_client.zcard(key)
            
            if current_requests >= self.rate_limit_requests:
                return True
            
            # Добавление текущего запроса
            await redis_client.zadd(key, {str(current_time): current_time})
            await redis_client.expire(key, self.rate_limit_window)
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки rate limit: {e}")
            # В случае ошибки Redis разрешаем запрос
            return False
    
    async def get_rate_limit_info(self, client_ip: str, endpoint: str) -> Dict:
        """Получение информации о текущем состоянии rate limit"""
        try:
            redis_client = await get_redis()
            key = f"rate_limit:{client_ip}:{endpoint}"
            current_time = int(time.time())
            window_start = current_time - self.rate_limit_window
            
            # Подсчет текущих запросов
            current_requests = await redis_client.zcard(key)
            remaining_requests = max(0, self.rate_limit_requests - current_requests)
            
            # Получение времени до сброса
            oldest_request = await redis_client.zrange(key, 0, 0, withscores=True)
            reset_time = oldest_request[0][1] + self.rate_limit_window if oldest_request else current_time
            
            return {
                "limit": self.rate_limit_requests,
                "remaining": remaining_requests,
                "reset_time": reset_time,
                "window": self.rate_limit_window
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о rate limit: {e}")
            return {
                "limit": self.rate_limit_requests,
                "remaining": self.rate_limit_requests,
                "reset_time": int(time.time()) + self.rate_limit_window,
                "window": self.rate_limit_window
            }
