from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.core.database import get_db_write, get_db_read, db_manager
from app.models.annotator_session import AnnotatorSession
from app.models.vector_clock import VectorClock, vector_clock_manager
from app.core.monitoring import session_monitor, monitor_performance
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate

router = APIRouter()

@router.post("/create", response_model=SessionResponse)
@monitor_performance("session_create")
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db_write)
):
    """Создать новую сессию разметчика"""
    try:
        # Генерация уникального ID сессии
        session_id = str(uuid.uuid4())
        
        # Создание записи сессии в БД
        db_session = AnnotatorSession(
            session_id=session_id,
            annotator_id=session_data.annotator_id,
            current_replica='master',
            is_active=True
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        # Создание vector clock для сессии
        vector_clock = vector_clock_manager.create_clock(session_id, 'master')
        
        # Сохранение vector clock в БД
        db_clock = VectorClock(
            session_id=session_id,
            clock_data=vector_clock
        )
        db.add(db_clock)
        db.commit()
        
        # Логирование события
        session_monitor.session_created(session_id, session_data.annotator_id, 'master')
        
        return SessionResponse(
            session_id=session_id,
            annotator_id=session_data.annotator_id,
            current_replica='master',
            is_active=True,
            vector_clock=vector_clock
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get("/{session_id}", response_model=SessionResponse)
@monitor_performance("session_get")
async def get_session(
    session_id: str,
    db: Session = Depends(get_db_read)
):
    """Получить информацию о сессии"""
    try:
        # Поиск сессии в БД
        db_session = db.query(AnnotatorSession).filter(
            AnnotatorSession.session_id == session_id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Получение vector clock
        vector_clock = vector_clock_manager.get_clock(session_id)
        
        return SessionResponse(
            session_id=db_session.session_id,
            annotator_id=db_session.annotator_id,
            current_replica=db_session.current_replica,
            is_active=db_session.is_active,
            vector_clock=vector_clock,
            last_activity=db_session.last_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )

@router.put("/{session_id}/switch-replica")
@monitor_performance("session_switch_replica")
async def switch_replica(
    session_id: str,
    replica: str,
    db: Session = Depends(get_db_write)
):
    """Переключить сессию на другую реплику"""
    try:
        # Поиск сессии
        db_session = db.query(AnnotatorSession).filter(
            AnnotatorSession.session_id == session_id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Проверка доступности реплики
        if not db_manager.replica_health.get(replica, False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Replica {replica} is not available"
            )
        
        old_replica = db_session.current_replica
        db_session.switch_replica(replica)
        db.commit()
        
        # Логирование события
        session_monitor.replica_switched(session_id, old_replica, replica)
        
        return {"message": f"Switched to replica {replica}", "old_replica": old_replica}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to switch replica: {str(e)}"
        )

@router.put("/{session_id}/update-activity")
@monitor_performance("session_update_activity")
async def update_activity(
    session_id: str,
    db: Session = Depends(get_db_write)
):
    """Обновить время последней активности сессии"""
    try:
        db_session = db.query(AnnotatorSession).filter(
            AnnotatorSession.session_id == session_id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        db_session.update_activity()
        db.commit()
        
        return {"message": "Activity updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update activity: {str(e)}"
        )

@router.delete("/{session_id}")
@monitor_performance("session_end")
async def end_session(
    session_id: str,
    db: Session = Depends(get_db_write)
):
    """Завершить сессию"""
    try:
        db_session = db.query(AnnotatorSession).filter(
            AnnotatorSession.session_id == session_id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Вычисление длительности сессии
        duration = (datetime.utcnow() - db_session.created_at).total_seconds()
        
        db_session.deactivate()
        db.commit()
        
        # Логирование события
        session_monitor.session_ended(session_id, db_session.annotator_id, duration)
        
        return {"message": "Session ended successfully", "duration": duration}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )

@router.get("/", response_model=List[SessionResponse])
@monitor_performance("sessions_list")
async def list_sessions(
    active_only: bool = True,
    db: Session = Depends(get_db_read)
):
    """Получить список всех сессий"""
    try:
        query = db.query(AnnotatorSession)
        if active_only:
            query = query.filter(AnnotatorSession.is_active == True)
        
        sessions = query.all()
        
        result = []
        for session in sessions:
            vector_clock = vector_clock_manager.get_clock(session.session_id)
            result.append(SessionResponse(
                session_id=session.session_id,
                annotator_id=session.annotator_id,
                current_replica=session.current_replica,
                is_active=session.is_active,
                vector_clock=vector_clock,
                last_activity=session.last_activity
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )
