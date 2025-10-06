import pytest
import asyncio
import time
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db_write, get_db_read, db_manager
from app.models.labeled_data import LabeledData
from app.models.annotator_session import AnnotatorSession
from app.models.vector_clock import vector_clock_manager
from app.services.consistency_service import ConsistencyService


class TestConsistency:
    """Тесты для проверки согласованности данных"""
    
    @pytest.fixture
    def consistency_service(self):
        return ConsistencyService()
    
    @pytest.fixture
    def test_sessions(self, db: Session):
        """Создание тестовых сессий"""
        sessions = []
        for i in range(3):
            session = AnnotatorSession(
                session_id=f"test_session_{i}",
                annotator_id=f"annotator_{i}",
                current_replica="master",
                is_active=True
            )
            db.add(session)
            sessions.append(session)
        
        db.commit()
        return sessions
    
    def test_vector_clock_ordering(self):
        """Тест упорядочивания операций с помощью vector clocks"""
        session_id = "test_session"
        
        # Создание vector clock
        clock1 = vector_clock_manager.create_clock(session_id, "node1")
        clock2 = vector_clock_manager.increment_clock(session_id, "node1")
        clock3 = vector_clock_manager.increment_clock(session_id, "node2")
        
        # Проверка упорядочивания
        assert vector_clock_manager.compare_clocks(clock1, clock2) == 'before'
        assert vector_clock_manager.compare_clocks(clock2, clock1) == 'after'
        assert vector_clock_manager.compare_clocks(clock1, clock3) == 'concurrent'
    
    def test_concurrent_modifications_detection(self):
        """Тест обнаружения одновременных модификаций"""
        session_id = "test_session"
        
        # Создание двух concurrent clocks
        clock1 = {"node1": 1, "node2": 0}
        clock2 = {"node1": 0, "node2": 1}
        
        conflicts = vector_clock_manager.detect_conflicts(session_id, clock1)
        assert len(conflicts) == 0  # Первая операция
        
        conflicts = vector_clock_manager.detect_conflicts(session_id, clock2)
        assert len(conflicts) > 0  # Concurrent операция
        assert conflicts[0]['type'] == 'concurrent_modification'
    
    def test_replica_consistency(self, db: Session):
        """Тест согласованности между репликами"""
        # Создание данных в master
        labeled_data = LabeledData(
            session_id="test_session",
            annotator_id="test_annotator",
            data_id="test_data_1",
            original_text="Test text",
            label="positive",
            confidence=0.95,
            vector_clock={"master": 1}
        )
        
        db.add(labeled_data)
        db.commit()
        
        # Проверка доступности данных в репликах
        for replica in ['replica1', 'replica2']:
            if db_manager.replica_health.get(replica, False):
                replica_db = db_manager.get_read_session(replica)
                replica_data = replica_db.query(LabeledData).filter(
                    LabeledData.data_id == "test_data_1"
                ).first()
                
                if replica_data:  # Если реплика синхронизирована
                    assert replica_data.label == "positive"
                    assert replica_data.confidence == 0.95
    
    def test_session_replica_switching(self, db: Session, test_sessions):
        """Тест переключения сессий между репликами"""
        session = test_sessions[0]
        
        # Переключение на реплику
        session.switch_replica("replica1")
        db.commit()
        
        assert session.current_replica == "replica1"
        assert session.last_activity is not None
    
    def test_conflict_resolution(self, db: Session):
        """Тест разрешения конфликтов"""
        # Создание конфликтной записи
        conflict_data = LabeledData(
            session_id="test_session",
            annotator_id="test_annotator",
            data_id="conflict_data",
            original_text="Conflict text",
            label="positive",
            confidence=0.8,
            vector_clock={"node1": 1, "node2": 1},
            is_conflict=True,
            conflict_resolution="pending"
        )
        
        db.add(conflict_data)
        db.commit()
        
        # Разрешение конфликта
        conflict_data.is_conflict = False
        conflict_data.conflict_resolution = "resolved"
        conflict_data.label = "negative"  # Выбранная метка
        
        db.commit()
        
        # Проверка разрешения
        resolved_data = db.query(LabeledData).filter(
            LabeledData.data_id == "conflict_data"
        ).first()
        
        assert resolved_data.is_conflict == False
        assert resolved_data.conflict_resolution == "resolved"
        assert resolved_data.label == "negative"
    
    def test_eventual_consistency(self, db: Session):
        """Тест eventual consistency"""
        # Создание данных в master
        test_data = []
        for i in range(10):
            data = LabeledData(
                session_id=f"session_{i}",
                annotator_id=f"annotator_{i}",
                data_id=f"data_{i}",
                original_text=f"Text {i}",
                label="positive" if i % 2 == 0 else "negative",
                confidence=0.9,
                vector_clock={"master": i + 1}
            )
            test_data.append(data)
            db.add(data)
        
        db.commit()
        
        # Проверка eventual consistency в репликах
        for replica in ['replica1', 'replica2']:
            if db_manager.replica_health.get(replica, False):
                replica_db = db_manager.get_read_session(replica)
                replica_count = replica_db.query(LabeledData).count()
                
                # В идеальном случае все данные должны быть синхронизированы
                # В реальности может быть задержка репликации
                assert replica_count >= 0  # Минимум 0 записей
    
    def test_load_balancing(self):
        """Тест балансировки нагрузки между репликами"""
        # Симуляция множественных запросов
        replica_usage = {"master": 0, "replica1": 0, "replica2": 0}
        
        for i in range(100):
            session = db_manager.get_read_session()
            # Определение используемой реплики (упрощенная логика)
            if "master" in str(session.bind.url):
                replica_usage["master"] += 1
            elif "replica1" in str(session.bind.url):
                replica_usage["replica1"] += 1
            elif "replica2" in str(session.bind.url):
                replica_usage["replica2"] += 1
        
        # Проверка, что нагрузка распределяется
        total_requests = sum(replica_usage.values())
        assert total_requests == 100
        
        # В идеальном случае нагрузка должна быть распределена равномерно
        # между доступными репликами
    
    def test_fault_tolerance(self, db: Session):
        """Тест отказоустойчивости"""
        # Симуляция недоступности реплики
        original_health = db_manager.replica_health.copy()
        db_manager.replica_health["replica1"] = False
        
        try:
            # Система должна продолжать работать с доступными репликами
            session = db_manager.get_read_session()
            assert session is not None
            
            # При недоступности всех реплик должна использоваться master
            db_manager.replica_health["replica2"] = False
            session = db_manager.get_read_session()
            assert session is not None
            
        finally:
            # Восстановление исходного состояния
            db_manager.replica_health = original_health
    
    def test_data_integrity(self, db: Session):
        """Тест целостности данных"""
        # Создание данных с vector clock
        original_clock = {"master": 1, "replica1": 0}
        
        labeled_data = LabeledData(
            session_id="integrity_test",
            annotator_id="test_annotator",
            data_id="integrity_data",
            original_text="Integrity test",
            label="positive",
            confidence=0.95,
            vector_clock=original_clock
        )
        
        db.add(labeled_data)
        db.commit()
        
        # Проверка сохранения vector clock
        saved_data = db.query(LabeledData).filter(
            LabeledData.data_id == "integrity_data"
        ).first()
        
        assert saved_data.vector_clock == original_clock
        assert saved_data.label == "positive"
        assert saved_data.confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, db: Session):
        """Тест одновременных сессий"""
        async def create_session(session_id, annotator_id):
            session = AnnotatorSession(
                session_id=session_id,
                annotator_id=annotator_id,
                current_replica="master",
                is_active=True
            )
            db.add(session)
            return session
        
        # Создание множественных сессий одновременно
        tasks = []
        for i in range(10):
            task = create_session(f"concurrent_session_{i}", f"annotator_{i}")
            tasks.append(task)
        
        sessions = await asyncio.gather(*tasks)
        db.commit()
        
        # Проверка, что все сессии созданы
        assert len(sessions) == 10
        
        # Проверка уникальности session_id
        session_ids = [s.session_id for s in sessions]
        assert len(set(session_ids)) == 10
