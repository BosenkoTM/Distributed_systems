from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import os
from datetime import datetime

from app.core.database import get_db_write, get_db_read
from app.models.csv_file import CSVFile
from app.core.config import settings
from app.core.monitoring import monitor_performance

router = APIRouter()

@router.post("/upload", response_model=Dict[str, Any])
@monitor_performance("file_upload")
async def upload_csv_file(
    file: UploadFile = File(...),
    uploaded_by: str = "anonymous",
    db: Session = Depends(get_db_write)
):
    """Загрузить CSV файл для разметки"""
    try:
        # Проверка типа файла
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are allowed"
            )
        
        # Создание директории для загрузки
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Сохранение файла
        file_path = os.path.join(settings.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Чтение CSV для получения информации
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # Создание записи в БД
        db_file = CSVFile(
            filename=file.filename,
            file_path=file_path,
            total_rows=total_rows,
            uploaded_by=uploaded_by,
            status='uploaded'
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "total_rows": db_file.total_rows,
            "status": db_file.status,
            "uploaded_at": db_file.uploaded_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
@monitor_performance("files_list")
async def list_files(
    db: Session = Depends(get_db_read)
):
    """Получить список загруженных файлов"""
    try:
        files = db.query(CSVFile).all()
        
        result = []
        for file in files:
            result.append({
                "id": file.id,
                "filename": file.filename,
                "total_rows": file.total_rows,
                "processed_rows": file.processed_rows,
                "uploaded_by": file.uploaded_by,
                "uploaded_at": file.uploaded_at.isoformat(),
                "status": file.status,
                "progress_percentage": (file.processed_rows / file.total_rows * 100) if file.total_rows > 0 else 0
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )

@router.get("/{file_id}/data")
@monitor_performance("file_get_data")
async def get_file_data(
    file_id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db_read)
):
    """Получить данные из CSV файла"""
    try:
        # Поиск файла в БД
        db_file = db.query(CSVFile).filter(CSVFile.id == file_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Чтение CSV файла
        df = pd.read_csv(db_file.file_path)
        
        # Применение пагинации
        paginated_df = df.iloc[offset:offset + limit]
        
        return {
            "data": paginated_df.to_dict('records'),
            "total_rows": len(df),
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < len(df)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file data: {str(e)}"
        )

@router.put("/{file_id}/progress")
@monitor_performance("file_update_progress")
async def update_file_progress(
    file_id: int,
    processed_rows: int,
    db: Session = Depends(get_db_write)
):
    """Обновить прогресс обработки файла"""
    try:
        db_file = db.query(CSVFile).filter(CSVFile.id == file_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        db_file.update_progress(processed_rows)
        db.commit()
        
        return {
            "message": "Progress updated successfully",
            "processed_rows": db_file.processed_rows,
            "total_rows": db_file.total_rows,
            "progress_percentage": (db_file.processed_rows / db_file.total_rows * 100) if db_file.total_rows > 0 else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )

@router.delete("/{file_id}")
@monitor_performance("file_delete")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db_write)
):
    """Удалить файл"""
    try:
        db_file = db.query(CSVFile).filter(CSVFile.id == file_id).first()
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Удаление файла с диска
        if os.path.exists(db_file.file_path):
            os.remove(db_file.file_path)
        
        # Удаление записи из БД
        db.delete(db_file)
        db.commit()
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
