from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Dict, Any


class CSVFile(Base):
    __tablename__ = "csv_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    total_rows = Column(Integer, nullable=False)
    processed_rows = Column(Integer, default=0)
    uploaded_by = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default='uploaded')
    
    def __repr__(self):
        return f"<CSVFile(id={self.id}, filename={self.filename}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "total_rows": self.total_rows,
            "processed_rows": self.processed_rows,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "status": self.status,
            "progress_percentage": (self.processed_rows / self.total_rows * 100) if self.total_rows > 0 else 0
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CSVFile':
        """Создание из словаря"""
        return cls(
            filename=data.get('filename'),
            file_path=data.get('file_path'),
            total_rows=data.get('total_rows', 0),
            processed_rows=data.get('processed_rows', 0),
            uploaded_by=data.get('uploaded_by'),
            status=data.get('status', 'uploaded')
        )
    
    def update_progress(self, processed_rows: int):
        """Обновить прогресс обработки"""
        self.processed_rows = processed_rows
        if self.processed_rows >= self.total_rows:
            self.status = 'completed'
    
    def set_status(self, status: str):
        """Установить статус файла"""
        self.status = status
