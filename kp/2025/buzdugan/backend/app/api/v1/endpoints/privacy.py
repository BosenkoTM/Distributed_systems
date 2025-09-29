"""
Эндпоинты для управления политиками приватности
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog

from app.core.database import get_db
from app.models.privacy_policy import PrivacyPolicy
from app.services.privacy_service import PrivacyService
from app.services.auth_service import AuthService, get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic модели
class PrivacyPolicyCreate(BaseModel):
    name: str
    description: str
    policy_type: str
    parameters: Dict[str, Any]

class PrivacyPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PrivacyPolicyResponse(BaseModel):
    id: str
    name: str
    description: str
    policy_type: str
    parameters: Dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str

class AnonymizationRequest(BaseModel):
    table_name: str
    query: str
    policy_id: str
    user_context: Optional[Dict[str, Any]] = None

class AnonymizationResponse(BaseModel):
    anonymized_data: List[Dict[str, Any]]
    applied_policy: str
    privacy_metrics: Dict[str, Any]

@router.get("/policies", response_model=List[PrivacyPolicyResponse])
async def get_privacy_policies(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение списка политик приватности"""
    try:
        privacy_service = PrivacyService(db)
        policies = await privacy_service.get_all_policies()
        
        return [
            PrivacyPolicyResponse(
                id=str(policy.id),
                name=policy.name,
                description=policy.description,
                policy_type=policy.policy_type,
                parameters=policy.parameters,
                is_active=policy.is_active,
                created_at=policy.created_at.isoformat(),
                updated_at=policy.updated_at.isoformat()
            )
            for policy in policies
        ]
        
    except Exception as e:
        logger.error(f"Ошибка получения политик приватности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/policies", response_model=PrivacyPolicyResponse)
async def create_privacy_policy(
    policy_data: PrivacyPolicyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создание новой политики приватности"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "analyst"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для создания политик"
            )
        
        privacy_service = PrivacyService(db)
        policy = await privacy_service.create_policy(
            name=policy_data.name,
            description=policy_data.description,
            policy_type=policy_data.policy_type,
            parameters=policy_data.parameters,
            created_by=current_user.id
        )
        
        logger.info("Создана новая политика приватности", 
                   policy_name=policy.name, 
                   created_by=current_user.username)
        
        return PrivacyPolicyResponse(
            id=str(policy.id),
            name=policy.name,
            description=policy.description,
            policy_type=policy.policy_type,
            parameters=policy.parameters,
            is_active=policy.is_active,
            created_at=policy.created_at.isoformat(),
            updated_at=policy.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания политики приватности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.put("/policies/{policy_id}", response_model=PrivacyPolicyResponse)
async def update_privacy_policy(
    policy_id: str,
    policy_data: PrivacyPolicyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновление политики приватности"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "analyst"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для изменения политик"
            )
        
        privacy_service = PrivacyService(db)
        policy = await privacy_service.update_policy(
            policy_id=policy_id,
            **policy_data.dict(exclude_unset=True)
        )
        
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Политика не найдена"
            )
        
        logger.info("Обновлена политика приватности", 
                   policy_id=policy_id, 
                   updated_by=current_user.username)
        
        return PrivacyPolicyResponse(
            id=str(policy.id),
            name=policy.name,
            description=policy.description,
            policy_type=policy.policy_type,
            parameters=policy.parameters,
            is_active=policy.is_active,
            created_at=policy.created_at.isoformat(),
            updated_at=policy.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления политики приватности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.delete("/policies/{policy_id}")
async def delete_privacy_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Удаление политики приватности"""
    try:
        # Проверка прав доступа
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для удаления политик"
            )
        
        privacy_service = PrivacyService(db)
        success = await privacy_service.delete_policy(policy_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Политика не найдена"
            )
        
        logger.info("Удалена политика приватности", 
                   policy_id=policy_id, 
                   deleted_by=current_user.username)
        
        return {"message": "Политика успешно удалена"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления политики приватности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_data(
    request: AnonymizationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Анонимизация данных согласно политике приватности"""
    try:
        privacy_service = PrivacyService(db)
        
        # Получение политики
        policy = await privacy_service.get_policy_by_id(request.policy_id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Политика не найдена"
            )
        
        # Применение анонимизации
        result = await privacy_service.apply_anonymization(
            table_name=request.table_name,
            query=request.query,
            policy=policy,
            user_context=request.user_context
        )
        
        logger.info("Применена анонимизация данных", 
                   policy_name=policy.name,
                   table_name=request.table_name,
                   user=current_user.username)
        
        return AnonymizationResponse(
            anonymized_data=result["data"],
            applied_policy=policy.name,
            privacy_metrics=result["metrics"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка анонимизации данных: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/metrics")
async def get_privacy_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение метрик приватности"""
    try:
        privacy_service = PrivacyService(db)
        metrics = await privacy_service.get_privacy_metrics()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Ошибка получения метрик приватности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
