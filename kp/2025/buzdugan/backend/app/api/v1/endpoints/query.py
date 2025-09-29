"""
Эндпоинты для выполнения SQL запросов с применением политик приватности
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog

from app.core.database import get_db
from app.services.query_service import QueryService
from app.services.auth_service import get_current_user
from app.services.privacy_service import PrivacyService

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic модели
class QueryRequest(BaseModel):
    sql: str
    privacy_policy_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: int
    privacy_policy_applied: Optional[str] = None
    privacy_metrics: Optional[Dict[str, Any]] = None

class QueryValidationResponse(BaseModel):
    is_valid: bool
    query_type: str
    tables_accessed: List[str]
    potential_privacy_risks: List[str]
    recommendations: List[str]

@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Выполнение SQL запроса с применением политик приватности"""
    try:
        query_service = QueryService(db)
        privacy_service = PrivacyService(db)
        
        # Валидация запроса
        validation_result = await query_service.validate_query(request.sql)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невалидный SQL запрос: {validation_result['errors']}"
            )
        
        # Проверка прав доступа к таблицам
        access_check = await query_service.check_table_access(
            validation_result["tables_accessed"], 
            current_user
        )
        if not access_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Нет доступа к таблицам: {access_check['denied_tables']}"
            )
        
        # Получение политики приватности
        privacy_policy = None
        if request.privacy_policy_id:
            privacy_policy = await privacy_service.get_policy_by_id(request.privacy_policy_id)
            if not privacy_policy:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Политика приватности не найдена"
                )
        
        # Выполнение запроса
        result = await query_service.execute_query(
            sql=request.sql,
            privacy_policy=privacy_policy,
            user=current_user,
            parameters=request.parameters
        )
        
        logger.info("Выполнен SQL запрос", 
                   user=current_user.username,
                   query_type=validation_result["query_type"],
                   tables=validation_result["tables_accessed"],
                   privacy_policy=privacy_policy.name if privacy_policy else None)
        
        return QueryResponse(
            data=result["data"],
            columns=result["columns"],
            row_count=result["row_count"],
            execution_time_ms=result["execution_time_ms"],
            privacy_policy_applied=privacy_policy.name if privacy_policy else None,
            privacy_metrics=result.get("privacy_metrics")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка выполнения SQL запроса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/validate", response_model=QueryValidationResponse)
async def validate_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Валидация SQL запроса без выполнения"""
    try:
        query_service = QueryService(db)
        privacy_service = PrivacyService(db)
        
        # Валидация запроса
        validation_result = await query_service.validate_query(request.sql)
        
        # Анализ рисков приватности
        privacy_risks = await privacy_service.analyze_privacy_risks(
            request.sql,
            validation_result.get("tables_accessed", [])
        )
        
        # Генерация рекомендаций
        recommendations = await privacy_service.generate_recommendations(
            request.sql,
            privacy_risks
        )
        
        return QueryValidationResponse(
            is_valid=validation_result["is_valid"],
            query_type=validation_result.get("query_type", "unknown"),
            tables_accessed=validation_result.get("tables_accessed", []),
            potential_privacy_risks=privacy_risks,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Ошибка валидации SQL запроса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/history")
async def get_query_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение истории SQL запросов пользователя"""
    try:
        query_service = QueryService(db)
        
        # Проверка прав доступа
        if current_user.role not in ["admin", "auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра истории запросов"
            )
        
        history = await query_service.get_query_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения истории запросов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/tables")
async def get_accessible_tables(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение списка доступных таблиц для пользователя"""
    try:
        query_service = QueryService(db)
        
        tables = await query_service.get_accessible_tables(current_user)
        
        return {"tables": tables}
        
    except Exception as e:
        logger.error(f"Ошибка получения списка таблиц: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/schema/{table_name}")
async def get_table_schema(
    table_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение схемы таблицы"""
    try:
        query_service = QueryService(db)
        
        # Проверка доступа к таблице
        access_check = await query_service.check_table_access([table_name], current_user)
        if not access_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к таблице"
            )
        
        schema = await query_service.get_table_schema(table_name)
        
        return schema
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения схемы таблицы: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
