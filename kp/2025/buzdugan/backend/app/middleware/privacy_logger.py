"""
Middleware для логирования операций с приватностью
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import structlog
from typing import Dict, Any

from app.core.database import get_db
from app.core.monitoring import record_privacy_policy, record_anonymization

logger = structlog.get_logger(__name__)

class PrivacyLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования операций с приватностью"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logger
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Получение информации о запросе
        request_info = await self.extract_request_info(request)
        
        # Выполнение запроса
        response = await call_next(request)
        
        # Вычисление времени выполнения
        process_time = time.time() - start_time
        
        # Логирование запроса
        await self.log_request(request_info, response, process_time)
        
        return response
    
    async def extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Извлечение информации о запросе"""
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self.get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": time.time()
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Получение IP адреса клиента"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def log_request(self, request_info: Dict[str, Any], response: Response, process_time: float):
        """Логирование запроса"""
        try:
            # Определение типа операции
            operation_type = self.determine_operation_type(request_info)
            
            # Логирование в структурированном формате
            log_data = {
                "request_id": f"req_{int(time.time() * 1000)}",
                "method": request_info["method"],
                "path": request_info["path"],
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": request_info["client_ip"],
                "user_agent": request_info["user_agent"],
                "operation_type": operation_type,
                "timestamp": request_info["timestamp"]
            }
            
            # Добавление информации о приватности если применимо
            if self.is_privacy_related(request_info):
                privacy_info = await self.extract_privacy_info(request_info, response)
                log_data.update(privacy_info)
                
                # Запись метрик
                if privacy_info.get("privacy_policy_applied"):
                    record_privacy_policy(
                        privacy_info["policy_type"],
                        privacy_info["policy_name"]
                    )
                
                if privacy_info.get("anonymization_performed"):
                    record_anonymization(
                        privacy_info["anonymization_type"],
                        privacy_info["table_name"]
                    )
            
            # Логирование в зависимости от уровня
            if response.status_code >= 400:
                self.logger.error("HTTP request error", **log_data)
            elif self.is_privacy_related(request_info):
                self.logger.info("Privacy-related request", **log_data)
            else:
                self.logger.debug("HTTP request", **log_data)
                
        except Exception as e:
            self.logger.error(f"Ошибка логирования запроса: {e}")
    
    def determine_operation_type(self, request_info: Dict[str, Any]) -> str:
        """Определение типа операции"""
        path = request_info["path"]
        method = request_info["method"]
        
        if "/api/v1/query" in path:
            return "database_query"
        elif "/api/v1/privacy" in path:
            return "privacy_management"
        elif "/api/v1/auth" in path:
            return "authentication"
        elif "/api/v1/admin" in path:
            return "administration"
        else:
            return "general"
    
    def is_privacy_related(self, request_info: Dict[str, Any]) -> bool:
        """Проверка, связан ли запрос с приватностью"""
        path = request_info["path"]
        return any(keyword in path for keyword in [
            "privacy", "anonymize", "k-anonymity", "l-diversity", 
            "differential-privacy", "query", "data"
        ])
    
    async def extract_privacy_info(self, request_info: Dict[str, Any], response: Response) -> Dict[str, Any]:
        """Извлечение информации о приватности из запроса и ответа"""
        privacy_info = {}
        
        try:
            # Проверка заголовков на информацию о приватности
            privacy_policy = response.headers.get("X-Privacy-Policy")
            if privacy_policy:
                privacy_info["privacy_policy_applied"] = True
                privacy_info["policy_name"] = privacy_policy
            
            anonymization_type = response.headers.get("X-Anonymization-Type")
            if anonymization_type:
                privacy_info["anonymization_performed"] = True
                privacy_info["anonymization_type"] = anonymization_type
            
            table_name = response.headers.get("X-Table-Name")
            if table_name:
                privacy_info["table_name"] = table_name
            
            # Анализ тела запроса для SQL запросов
            if request_info["method"] == "POST" and "/query" in request_info["path"]:
                # Здесь можно добавить парсинг SQL для извлечения дополнительной информации
                privacy_info["sql_query"] = True
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения информации о приватности: {e}")
        
        return privacy_info
