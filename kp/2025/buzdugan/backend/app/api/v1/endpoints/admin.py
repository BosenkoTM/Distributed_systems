"""
Эндпоинты для административного управления
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog

from app.core.database import get_db
from app.services.admin_service import AdminService
from app.services.auth_service import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic модели
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str

class SystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_queries: int
    privacy_policies_count: int
    system_health: Dict[str, Any]

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение списка пользователей"""
    try:
        # Проверка прав доступа
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра пользователей"
            )
        
        admin_service = AdminService(db)
        users = await admin_service.get_users(limit=limit, offset=offset)
        
        return [
            UserResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat()
            )
            for user in users
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения списка пользователей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создание нового пользователя"""
    try:
        # Проверка прав доступа
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для создания пользователей"
            )
        
        admin_service = AdminService(db)
        user = await admin_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        logger.info("Создан новый пользователь", 
                   username=user.username, 
                   role=user.role,
                   created_by=current_user.username)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновление пользователя"""
    try:
        # Проверка прав доступа
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для изменения пользователей"
            )
        
        admin_service = AdminService(db)
        user = await admin_service.update_user(
            user_id=user_id,
            **user_data.dict(exclude_unset=True)
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        logger.info("Обновлен пользователь", 
                   user_id=user_id, 
                   updated_by=current_user.username)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Удаление пользователя"""
    try:
        # Проверка прав доступа
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для удаления пользователей"
            )
        
        # Запрет удаления самого себя
        if str(current_user.id) == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить самого себя"
            )
        
        admin_service = AdminService(db)
        success = await admin_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        logger.info("Удален пользователь", 
                   user_id=user_id, 
                   deleted_by=current_user.username)
        
        return {"message": "Пользователь успешно удален"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение статистики системы"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра статистики"
            )
        
        admin_service = AdminService(db)
        stats = await admin_service.get_system_stats()
        
        return SystemStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения статистики системы: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/logs")
async def get_system_logs(
    log_type: str = "all",
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получение системных логов"""
    try:
        # Проверка прав доступа
        if current_user.role not in ["admin", "auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра логов"
            )
        
        admin_service = AdminService(db)
        logs = await admin_service.get_system_logs(
            log_type=log_type,
            limit=limit,
            offset=offset
        )
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения системных логов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/backup")
async def create_backup(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создание резервной копии системы"""
    try:
        # Проверка прав доступа
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для создания резервных копий"
            )
        
        admin_service = AdminService(db)
        backup_info = await admin_service.create_backup()
        
        logger.info("Создана резервная копия", 
                   backup_id=backup_info["backup_id"],
                   created_by=current_user.username)
        
        return backup_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания резервной копии: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
