from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.models.labeled_data import LabeledData
from app.models.annotator_session import AnnotatorSession
from app.models.vector_clock import vector_clock_manager
from app.core.database import db_manager
from app.core.monitoring import metrics

logger = logging.getLogger(__name__)


class ConsistencyService:
    """Сервис для обеспечения согласованности данных"""
    
    def __init__(self):
        self.conflict_resolution_strategies = {
            'last_write_wins': self._last_write_wins,
            'manual_resolution': self._manual_resolution,
            'confidence_based': self._confidence_based_resolution
        }
    
    def check_consistency(self, session_id: str, db: Session) -> Dict[str, Any]:
        """Проверить согласованность данных для сессии"""
        try:
            # Получение всех записей сессии
            labeled_data = db.query(LabeledData).filter(
                LabeledData.session_id == session_id
            ).all()
            
            # Проверка vector clocks
            clock_consistency = self._check_clock_consistency(labeled_data)
            
            # Проверка конфликтов
            conflicts = self._detect_data_conflicts(labeled_data)
            
            # Проверка репликации
            replication_status = self._check_replication_status(session_id)
            
            return {
                "session_id": session_id,
                "total_records": len(labeled_data),
                "clock_consistency": clock_consistency,
                "conflicts": conflicts,
                "replication_status": replication_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Consistency check failed for session {session_id}: {e}")
            raise
    
    def _check_clock_consistency(self, labeled_data: List[LabeledData]) -> Dict[str, Any]:
        """Проверить согласованность vector clocks"""
        if not labeled_data:
            return {"status": "empty", "issues": []}
        
        issues = []
        clocks = [item.vector_clock for item in labeled_data]
        
        # Проверка на concurrent операции
        for i, clock1 in enumerate(clocks):
            for j, clock2 in enumerate(clocks[i+1:], i+1):
                comparison = vector_clock_manager.compare_clocks(clock1, clock2)
                if comparison == 'concurrent':
                    issues.append({
                        "type": "concurrent_operations",
                        "record1": i,
                        "record2": j,
                        "clock1": clock1,
                        "clock2": clock2
                    })
        
        return {
            "status": "consistent" if not issues else "inconsistent",
            "issues": issues,
            "total_clocks": len(clocks)
        }
    
    def _detect_data_conflicts(self, labeled_data: List[LabeledData]) -> List[Dict[str, Any]]:
        """Обнаружить конфликты в данных"""
        conflicts = []
        
        # Группировка по data_id для поиска конфликтов
        data_groups = {}
        for item in labeled_data:
            if item.data_id not in data_groups:
                data_groups[item.data_id] = []
            data_groups[item.data_id].append(item)
        
        # Поиск конфликтов в каждой группе
        for data_id, items in data_groups.items():
            if len(items) > 1:
                # Проверка на разные метки для одного data_id
                labels = set(item.label for item in items)
                if len(labels) > 1:
                    conflicts.append({
                        "type": "label_conflict",
                        "data_id": data_id,
                        "conflicting_labels": list(labels),
                        "records": [item.id for item in items]
                    })
        
        return conflicts
    
    def _check_replication_status(self, session_id: str) -> Dict[str, Any]:
        """Проверить статус репликации"""
        replica_status = {}
        
        for replica_name, is_healthy in db_manager.replica_health.items():
            replica_status[replica_name] = {
                "healthy": is_healthy,
                "last_check": datetime.utcnow().isoformat()
            }
        
        return {
            "replicas": replica_status,
            "overall_status": "healthy" if all(
                status["healthy"] for status in replica_status.values()
            ) else "degraded"
        }
    
    def resolve_conflicts(
        self, 
        session_id: str, 
        strategy: str = 'last_write_wins',
        db: Session = None
    ) -> Dict[str, Any]:
        """Разрешить конфликты в сессии"""
        if strategy not in self.conflict_resolution_strategies:
            raise ValueError(f"Unknown conflict resolution strategy: {strategy}")
        
        try:
            # Получение конфликтных записей
            conflicts = db.query(LabeledData).filter(
                LabeledData.session_id == session_id,
                LabeledData.is_conflict == True
            ).all()
            
            if not conflicts:
                return {"message": "No conflicts found", "resolved": 0}
            
            # Применение стратегии разрешения
            resolver = self.conflict_resolution_strategies[strategy]
            resolved_count = resolver(conflicts, db)
            
            # Логирование события
            metrics.record_event("conflicts_resolved", {
                "session_id": session_id,
                "strategy": strategy,
                "resolved_count": resolved_count
            })
            
            return {
                "message": f"Resolved {resolved_count} conflicts using {strategy}",
                "resolved": resolved_count,
                "strategy": strategy
            }
            
        except Exception as e:
            logger.error(f"Conflict resolution failed for session {session_id}: {e}")
            raise
    
    def _last_write_wins(self, conflicts: List[LabeledData], db: Session) -> int:
        """Стратегия: последняя запись побеждает"""
        resolved = 0
        
        # Группировка по data_id
        data_groups = {}
        for conflict in conflicts:
            if conflict.data_id not in data_groups:
                data_groups[conflict.data_id] = []
            data_groups[conflict.data_id].append(conflict)
        
        for data_id, items in data_groups.items():
            # Сортировка по времени обновления (последняя запись)
            latest_item = max(items, key=lambda x: x.updated_at)
            
            # Удаление остальных записей
            for item in items:
                if item.id != latest_item.id:
                    db.delete(item)
                    resolved += 1
                else:
                    # Снятие флага конфликта с оставшейся записи
                    item.is_conflict = False
                    item.conflict_resolution = 'last_write_wins'
        
        db.commit()
        return resolved
    
    def _manual_resolution(self, conflicts: List[LabeledData], db: Session) -> int:
        """Стратегия: ручное разрешение (требует дополнительных данных)"""
        # В реальной реализации здесь была бы логика для ручного разрешения
        # Пока просто снимаем флаги конфликтов
        resolved = 0
        
        for conflict in conflicts:
            conflict.is_conflict = False
            conflict.conflict_resolution = 'manual'
            resolved += 1
        
        db.commit()
        return resolved
    
    def _confidence_based_resolution(self, conflicts: List[LabeledData], db: Session) -> int:
        """Стратегия: разрешение на основе уверенности"""
        resolved = 0
        
        # Группировка по data_id
        data_groups = {}
        for conflict in conflicts:
            if conflict.data_id not in data_groups:
                data_groups[conflict.data_id] = []
            data_groups[conflict.data_id].append(conflict)
        
        for data_id, items in data_groups.items():
            # Выбор записи с наибольшей уверенностью
            best_item = max(items, key=lambda x: float(x.confidence or 0))
            
            # Удаление остальных записей
            for item in items:
                if item.id != best_item.id:
                    db.delete(item)
                    resolved += 1
                else:
                    # Снятие флага конфликта с оставшейся записи
                    item.is_conflict = False
                    item.conflict_resolution = 'confidence_based'
        
        db.commit()
        return resolved
    
    def monitor_consistency(self, check_interval: int = 300) -> Dict[str, Any]:
        """Мониторинг согласованности системы"""
        try:
            # Получение активных сессий
            active_sessions = db_manager.get_read_session().query(AnnotatorSession).filter(
                AnnotatorSession.is_active == True
            ).all()
            
            consistency_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_active_sessions": len(active_sessions),
                "sessions_checked": 0,
                "conflicts_found": 0,
                "replica_health": db_manager.replica_health,
                "overall_status": "healthy"
            }
            
            # Проверка каждой активной сессии
            for session in active_sessions:
                try:
                    session_consistency = self.check_consistency(session.session_id, db_manager.get_read_session())
                    consistency_report["sessions_checked"] += 1
                    
                    if session_consistency["conflicts"]:
                        consistency_report["conflicts_found"] += len(session_consistency["conflicts"])
                        consistency_report["overall_status"] = "degraded"
                        
                except Exception as e:
                    logger.error(f"Failed to check consistency for session {session.session_id}: {e}")
                    consistency_report["overall_status"] = "error"
            
            # Запись метрик
            metrics.set_gauge("consistency.active_sessions", len(active_sessions))
            metrics.set_gauge("consistency.conflicts", consistency_report["conflicts_found"])
            
            return consistency_report
            
        except Exception as e:
            logger.error(f"Consistency monitoring failed: {e}")
            raise
    
    def cleanup_old_data(self, days_old: int = 30, db: Session = None) -> Dict[str, Any]:
        """Очистка старых данных"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Удаление старых неактивных сессий
            old_sessions = db.query(AnnotatorSession).filter(
                AnnotatorSession.is_active == False,
                AnnotatorSession.last_activity < cutoff_date
            ).all()
            
            sessions_deleted = len(old_sessions)
            for session in old_sessions:
                db.delete(session)
            
            # Удаление старых разметок
            old_labeled_data = db.query(LabeledData).filter(
                LabeledData.created_at < cutoff_date,
                LabeledData.is_conflict == False
            ).all()
            
            data_deleted = len(old_labeled_data)
            for data in old_labeled_data:
                db.delete(data)
            
            db.commit()
            
            return {
                "message": f"Cleaned up data older than {days_old} days",
                "sessions_deleted": sessions_deleted,
                "labeled_data_deleted": data_deleted,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            db.rollback()
            raise
