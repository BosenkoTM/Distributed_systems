from sqlalchemy import Column, Integer, String, Text, DECIMAL, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Dict, Any, Optional


class LabeledData(Base):
    __tablename__ = "labeled_data"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    annotator_id = Column(String(255), nullable=False, index=True)
    data_id = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    label = Column(String(255), nullable=False)
    confidence = Column(DECIMAL(3, 2), default=0.0)
    vector_clock = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_conflict = Column(Boolean, default=False)
    conflict_resolution = Column(String(50), default='pending')
    
    def __repr__(self):
        return f"<LabeledData(id={self.id}, session_id={self.session_id}, label={self.label})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "annotator_id": self.annotator_id,
            "data_id": self.data_id,
            "original_text": self.original_text,
            "label": self.label,
            "confidence": float(self.confidence) if self.confidence else 0.0,
            "vector_clock": self.vector_clock,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_conflict": self.is_conflict,
            "conflict_resolution": self.conflict_resolution
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LabeledData':
        """Создание из словаря"""
        return cls(
            session_id=data.get('session_id'),
            annotator_id=data.get('annotator_id'),
            data_id=data.get('data_id'),
            original_text=data.get('original_text'),
            label=data.get('label'),
            confidence=data.get('confidence', 0.0),
            vector_clock=data.get('vector_clock', {}),
            is_conflict=data.get('is_conflict', False),
            conflict_resolution=data.get('conflict_resolution', 'pending')
        )
