from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db_write, get_db_read
from app.models.labeled_data import LabeledData
from app.models.vector_clock import vector_clock_manager
from app.core.monitoring import session_monitor, monitor_performance
from app.schemas.labeling import (
    LabeledDataCreate, LabeledDataResponse, LabeledDataUpdate,
    ConflictResolution, BatchLabelingRequest, LabelingStats
)

router = APIRouter()

@router.post("/", response_model=LabeledDataResponse)
@monitor_performance("labeling_create")
async def create_labeled_data(
    labeled_data: LabeledDataCreate,
    db: Session = Depends(get_db_write)
):
    """Создать новую разметку данных"""
    try:
        # Проверка vector clock на конфликты
        conflicts = vector_clock_manager.detect_conflicts(
            labeled_data.session_id, 
            labeled_data.vector_clock
        )
        
        if conflicts:
            session_monitor.conflict_detected(labeled_data.session_id, "concurrent_modification")
        
        # Создание записи в БД
        db_labeled_data = LabeledData(
            session_id=labeled_data.session_id,
            annotator_id=labeled_data.annotator_id,
            data_id=labeled_data.data_id,
            original_text=labeled_data.original_text,
            label=labeled_data.label,
            confidence=labeled_data.confidence,
            vector_clock=labeled_data.vector_clock,
            is_conflict=len(conflicts) > 0
        )
        
        db.add(db_labeled_data)
        db.commit()
        db.refresh(db_labeled_data)
        
        # Обновление vector clock
        vector_clock_manager.merge_clocks(labeled_data.session_id, labeled_data.vector_clock)
        
        return LabeledDataResponse(
            id=db_labeled_data.id,
            session_id=db_labeled_data.session_id,
            annotator_id=db_labeled_data.annotator_id,
            data_id=db_labeled_data.data_id,
            original_text=db_labeled_data.original_text,
            label=db_labeled_data.label,
            confidence=db_labeled_data.confidence,
            vector_clock=db_labeled_data.vector_clock,
            created_at=db_labeled_data.created_at,
            updated_at=db_labeled_data.updated_at,
            is_conflict=db_labeled_data.is_conflict,
            conflict_resolution=db_labeled_data.conflict_resolution
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create labeled data: {str(e)}"
        )

@router.get("/{session_id}", response_model=List[LabeledDataResponse])
@monitor_performance("labeling_get_by_session")
async def get_labeled_data_by_session(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db_read)
):
    """Получить разметку данных по сессии"""
    try:
        labeled_data_list = db.query(LabeledData).filter(
            LabeledData.session_id == session_id
        ).offset(offset).limit(limit).all()
        
        result = []
        for item in labeled_data_list:
            result.append(LabeledDataResponse(
                id=item.id,
                session_id=item.session_id,
                annotator_id=item.annotator_id,
                data_id=item.data_id,
                original_text=item.original_text,
                label=item.label,
                confidence=item.confidence,
                vector_clock=item.vector_clock,
                created_at=item.created_at,
                updated_at=item.updated_at,
                is_conflict=item.is_conflict,
                conflict_resolution=item.conflict_resolution
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get labeled data: {str(e)}"
        )

@router.put("/{data_id}", response_model=LabeledDataResponse)
@monitor_performance("labeling_update")
async def update_labeled_data(
    data_id: int,
    update_data: LabeledDataUpdate,
    db: Session = Depends(get_db_write)
):
    """Обновить разметку данных"""
    try:
        # Поиск записи
        db_labeled_data = db.query(LabeledData).filter(LabeledData.id == data_id).first()
        
        if not db_labeled_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Labeled data not found"
            )
        
        # Проверка vector clock на конфликты
        if update_data.vector_clock:
            conflicts = vector_clock_manager.detect_conflicts(
                db_labeled_data.session_id,
                update_data.vector_clock
            )
            
            if conflicts:
                session_monitor.conflict_detected(db_labeled_data.session_id, "concurrent_modification")
                db_labeled_data.is_conflict = True
        
        # Обновление полей
        if update_data.label is not None:
            db_labeled_data.label = update_data.label
        if update_data.confidence is not None:
            db_labeled_data.confidence = update_data.confidence
        if update_data.vector_clock is not None:
            db_labeled_data.vector_clock = update_data.vector_clock
        
        db.commit()
        db.refresh(db_labeled_data)
        
        # Обновление vector clock
        if update_data.vector_clock:
            vector_clock_manager.merge_clocks(
                db_labeled_data.session_id, 
                update_data.vector_clock
            )
        
        return LabeledDataResponse(
            id=db_labeled_data.id,
            session_id=db_labeled_data.session_id,
            annotator_id=db_labeled_data.annotator_id,
            data_id=db_labeled_data.data_id,
            original_text=db_labeled_data.original_text,
            label=db_labeled_data.label,
            confidence=db_labeled_data.confidence,
            vector_clock=db_labeled_data.vector_clock,
            created_at=db_labeled_data.created_at,
            updated_at=db_labeled_data.updated_at,
            is_conflict=db_labeled_data.is_conflict,
            conflict_resolution=db_labeled_data.conflict_resolution
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update labeled data: {str(e)}"
        )

@router.post("/batch", response_model=List[LabeledDataResponse])
@monitor_performance("labeling_batch")
async def batch_labeling(
    batch_request: BatchLabelingRequest,
    db: Session = Depends(get_db_write)
):
    """Пакетная разметка данных"""
    try:
        results = []
        
        for label_data in batch_request.labels:
            # Создание записи для каждого элемента
            db_labeled_data = LabeledData(
                session_id=batch_request.session_id,
                annotator_id=batch_request.annotator_id,
                data_id=label_data.get('data_id'),
                original_text=label_data.get('original_text'),
                label=label_data.get('label'),
                confidence=label_data.get('confidence', 0.0),
                vector_clock=label_data.get('vector_clock', {})
            )
            
            db.add(db_labeled_data)
            results.append(db_labeled_data)
        
        db.commit()
        
        # Обновление vector clock для всех записей
        for result in results:
            db.refresh(result)
            vector_clock_manager.merge_clocks(
                batch_request.session_id,
                result.vector_clock
            )
        
        # Преобразование в response format
        response_results = []
        for item in results:
            response_results.append(LabeledDataResponse(
                id=item.id,
                session_id=item.session_id,
                annotator_id=item.annotator_id,
                data_id=item.data_id,
                original_text=item.original_text,
                label=item.label,
                confidence=item.confidence,
                vector_clock=item.vector_clock,
                created_at=item.created_at,
                updated_at=item.updated_at,
                is_conflict=item.is_conflict,
                conflict_resolution=item.conflict_resolution
            ))
        
        return response_results
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch labeling: {str(e)}"
        )

@router.get("/conflicts/{session_id}", response_model=List[LabeledDataResponse])
@monitor_performance("labeling_get_conflicts")
async def get_conflicts(
    session_id: str,
    db: Session = Depends(get_db_read)
):
    """Получить конфликты для сессии"""
    try:
        conflicts = db.query(LabeledData).filter(
            LabeledData.session_id == session_id,
            LabeledData.is_conflict == True
        ).all()
        
        result = []
        for conflict in conflicts:
            result.append(LabeledDataResponse(
                id=conflict.id,
                session_id=conflict.session_id,
                annotator_id=conflict.annotator_id,
                data_id=conflict.data_id,
                original_text=conflict.original_text,
                label=conflict.label,
                confidence=conflict.confidence,
                vector_clock=conflict.vector_clock,
                created_at=conflict.created_at,
                updated_at=conflict.updated_at,
                is_conflict=conflict.is_conflict,
                conflict_resolution=conflict.conflict_resolution
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conflicts: {str(e)}"
        )

@router.post("/resolve-conflict")
@monitor_performance("labeling_resolve_conflict")
async def resolve_conflict(
    resolution: ConflictResolution,
    db: Session = Depends(get_db_write)
):
    """Разрешить конфликт"""
    try:
        # Поиск конфликтной записи
        db_labeled_data = db.query(LabeledData).filter(
            LabeledData.id == resolution.conflict_id
        ).first()
        
        if not db_labeled_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conflict not found"
            )
        
        # Применение разрешения
        db_labeled_data.is_conflict = False
        db_labeled_data.conflict_resolution = resolution.resolution
        
        if resolution.chosen_label:
            db_labeled_data.label = resolution.chosen_label
        
        db.commit()
        
        return {"message": "Conflict resolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflict: {str(e)}"
        )

@router.get("/stats/{annotator_id}", response_model=LabelingStats)
@monitor_performance("labeling_get_stats")
async def get_labeling_stats(
    annotator_id: str,
    db: Session = Depends(get_db_read)
):
    """Получить статистику разметки для разметчика"""
    try:
        # Подсчет статистики
        total_labels = db.query(LabeledData).filter(
            LabeledData.annotator_id == annotator_id
        ).count()
        
        conflicts = db.query(LabeledData).filter(
            LabeledData.annotator_id == annotator_id,
            LabeledData.is_conflict == True
        ).count()
        
        # Средняя уверенность
        avg_confidence_result = db.query(LabeledData.confidence).filter(
            LabeledData.annotator_id == annotator_id
        ).all()
        
        avg_confidence = 0.0
        if avg_confidence_result:
            confidences = [float(item.confidence) for item in avg_confidence_result if item.confidence]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Последняя активность
        last_activity = db.query(LabeledData.updated_at).filter(
            LabeledData.annotator_id == annotator_id
        ).order_by(LabeledData.updated_at.desc()).first()
        
        return LabelingStats(
            total_labels=total_labels,
            conflicts=conflicts,
            avg_confidence=avg_confidence,
            last_activity=last_activity.updated_at if last_activity else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get labeling stats: {str(e)}"
        )
