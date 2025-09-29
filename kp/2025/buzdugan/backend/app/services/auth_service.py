"""
Сервис аутентификации и авторизации
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.core.redis_client import get_redis

logger = structlog.get_logger(__name__)
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            
            if not user:
                logger.warning("Попытка входа с несуществующим именем пользователя", username=username)
                return None
            
            if not user.is_active:
                logger.warning("Попытка входа неактивного пользователя", username=username)
                return None
            
            if not self.verify_password(password, user.password_hash):
                logger.warning("Неверный пароль", username=username)
                return None
            
            logger.info("Успешная аутентификация", username=username)
            return user
            
        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            return None
    
    def create_access_token(self, user: User) -> str:
        """Создание токена доступа"""
        try:
            to_encode = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role,
                "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            
            token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
            
            logger.info("Создан токен доступа", username=user.username)
            return token
            
        except Exception as e:
            logger.error(f"Ошибка создания токена: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка создания токена"
            )
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Получение текущего пользователя по токену"""
        try:
            # Проверка токена в Redis (blacklist)
            redis_client = await get_redis()
            is_blacklisted = await redis_client.get(f"blacklist:{token}")
            if is_blacklisted:
                logger.warning("Попытка использования заблокированного токена")
                return None
            
            # Декодирование токена
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                logger.warning("Токен не содержит user_id")
                return None
            
            # Получение пользователя из базы данных
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                logger.warning("Пользователь не найден или неактивен", user_id=user_id)
                return None
            
            return user
            
        except JWTError as e:
            logger.warning(f"Ошибка декодирования токена: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения текущего пользователя: {e}")
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """Отзыв токена (добавление в blacklist)"""
        try:
            redis_client = await get_redis()
            
            # Получение времени истечения токена
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            exp = payload.get("exp")
            
            if exp:
                # Добавление токена в blacklist до времени истечения
                ttl = exp - int(datetime.utcnow().timestamp())
                if ttl > 0:
                    await redis_client.setex(f"blacklist:{token}", ttl, "1")
            
            logger.info("Токен отозван")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отзыва токена: {e}")
            return False
    
    async def refresh_access_token(self, token: str) -> Optional[str]:
        """Обновление токена доступа"""
        try:
            # Получение текущего пользователя
            user = await self.get_current_user(token)
            if not user:
                return None
            
            # Создание нового токена
            new_token = self.create_access_token(user)
            
            # Отзыв старого токена
            await self.revoke_token(token)
            
            logger.info("Токен обновлен", username=user.username)
            return new_token
            
        except Exception as e:
            logger.error(f"Ошибка обновления токена: {e}")
            return None

# Зависимость для получения текущего пользователя
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя через dependency injection"""
    auth_service = AuthService(db)
    
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Зависимость для проверки роли
def require_role(required_role: str):
    """Декоратор для проверки роли пользователя"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль: {required_role}"
            )
        return current_user
    
    return role_checker

# Зависимость для проверки множественных ролей
def require_roles(required_roles: list):
    """Декоратор для проверки множественных ролей пользователя"""
    def roles_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуются роли: {', '.join(required_roles)}"
            )
        return current_user
    
    return roles_checker
