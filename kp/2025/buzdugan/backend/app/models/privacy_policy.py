"""
Модель политики приватности
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class PrivacyPolicy(Base):
    __tablename__ = "privacy_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    policy_type = Column(String(50), nullable=False, index=True)  # 'k_anonymity', 'l_diversity', 'differential_privacy'
    parameters = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи
    creator = relationship("User", back_populates="created_policies")
    
    def __repr__(self):
        return f"<PrivacyPolicy(id={self.id}, name='{self.name}', type='{self.policy_type}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type,
            "parameters": self.parameters,
            "is_active": self.is_active,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
