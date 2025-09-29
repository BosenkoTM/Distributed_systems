"""
Эндпоинты для аутентификации и авторизации
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.monitoring import record_failed_login

logger = structlog.get_logger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic модели для запросов
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    try:
        auth_service = AuthService(db)
        
        # Проверка учетных данных
        user = await auth_service.authenticate_user(
            login_data.username, 
            login_data.password
        )
        
        if not user:
            # Запись неудачной попытки входа
            record_failed_login(login_data.username, "unknown")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создание токена доступа
        access_token = await auth_service.create_access_token(user)
        
        logger.info("Успешная аутентификация", username=user.username)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Выход пользователя из системы"""
    try:
        auth_service = AuthService(db)
        await auth_service.revoke_token(credentials.credentials)
        
        logger.info("Пользователь вышел из системы")
        
        return {"message": "Успешный выход из системы"}
        
    except Exception as e:
        logger.error(f"Ошибка выхода из системы: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    try:
        auth_service = AuthService(db)
        
        # Проверка токена
        user = await auth_service.get_current_user(credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения информации о пользователе: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Обновление токена доступа"""
    try:
        auth_service = AuthService(db)
        
        # Обновление токена
        new_token = await auth_service.refresh_access_token(credentials.credentials)
        
        if not new_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен для обновления",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
