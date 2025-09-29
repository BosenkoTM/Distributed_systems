from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum
from sqlalchemy.sql import func
import enum
from database import Base

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    target_level = Column(String, default="Автоматически")
    augment = Column(Boolean, default=False)
    aug_factor = Column(Integer, default=1)
    user_id = Column(Integer, nullable=False)
    initial_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
