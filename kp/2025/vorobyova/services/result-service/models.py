from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.sql import func
from database import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")
    file_path = Column(String, nullable=False)
    initial_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
