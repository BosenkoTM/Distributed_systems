from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Dict, Any, Optional


class AnnotatorSession(Base):
    __tablename__ = "annotator_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    annotator_id = Column(String(255), nullable=False, index=True)
    current_replica = Column(String(50), default='master')
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AnnotatorSession(id={self.id}, session_id={self.session_id}, annotator_id={self.annotator_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "annotator_id": self.annotator_id,
            "current_replica": self.current_replica,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotatorSession':
        """Создание из словаря"""
        return cls(
            session_id=data.get('session_id'),
            annotator_id=data.get('annotator_id'),
            current_replica=data.get('current_replica', 'master'),
            is_active=data.get('is_active', True)
        )
    
    def update_activity(self):
        """Обновить время последней активности"""
        self.last_activity = datetime.utcnow()
    
    def switch_replica(self, new_replica: str):
        """Переключить на другую реплику"""
        self.current_replica = new_replica
        self.update_activity()
    
    def deactivate(self):
        """Деактивировать сессию"""
        self.is_active = False
        self.update_activity()
