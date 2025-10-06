from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Dict, Any, List
import json


class VectorClock(Base):
    __tablename__ = "vector_clocks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    clock_data = Column(JSON, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<VectorClock(id={self.id}, session_id={self.session_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "clock_data": self.clock_data,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorClock':
        """Создание из словаря"""
        return cls(
            session_id=data.get('session_id'),
            clock_data=data.get('clock_data', {})
        )


class VectorClockManager:
    """Менеджер для работы с vector clocks"""
    
    def __init__(self):
        self.clocks: Dict[str, Dict[str, int]] = {}
    
    def create_clock(self, session_id: str, node_id: str) -> Dict[str, int]:
        """Создать новый vector clock для сессии"""
        clock = {node_id: 0}
        self.clocks[session_id] = clock
        return clock.copy()
    
    def get_clock(self, session_id: str) -> Dict[str, int]:
        """Получить vector clock для сессии"""
        return self.clocks.get(session_id, {}).copy()
    
    def increment_clock(self, session_id: str, node_id: str) -> Dict[str, int]:
        """Увеличить счетчик для узла в vector clock"""
        if session_id not in self.clocks:
            self.clocks[session_id] = {}
        
        if node_id not in self.clocks[session_id]:
            self.clocks[session_id][node_id] = 0
        
        self.clocks[session_id][node_id] += 1
        return self.clocks[session_id].copy()
    
    def merge_clocks(self, session_id: str, other_clock: Dict[str, int]) -> Dict[str, int]:
        """Объединить vector clocks (максимум по каждому узлу)"""
        if session_id not in self.clocks:
            self.clocks[session_id] = {}
        
        for node_id, timestamp in other_clock.items():
            if node_id not in self.clocks[session_id]:
                self.clocks[session_id][node_id] = timestamp
            else:
                self.clocks[session_id][node_id] = max(
                    self.clocks[session_id][node_id], 
                    timestamp
                )
        
        return self.clocks[session_id].copy()
    
    def compare_clocks(self, clock1: Dict[str, int], clock2: Dict[str, int]) -> str:
        """
        Сравнить два vector clocks
        Возвращает: 'before', 'after', 'concurrent', 'equal'
        """
        all_nodes = set(clock1.keys()) | set(clock2.keys())
        
        clock1_before = False
        clock2_before = False
        
        for node in all_nodes:
            ts1 = clock1.get(node, 0)
            ts2 = clock2.get(node, 0)
            
            if ts1 < ts2:
                clock1_before = True
            elif ts1 > ts2:
                clock2_before = True
        
        if clock1_before and not clock2_before:
            return 'before'
        elif clock2_before and not clock1_before:
            return 'after'
        elif not clock1_before and not clock2_before:
            return 'equal'
        else:
            return 'concurrent'
    
    def detect_conflicts(self, session_id: str, new_clock: Dict[str, int]) -> List[Dict[str, Any]]:
        """Обнаружить конфликты на основе vector clocks"""
        current_clock = self.get_clock(session_id)
        if not current_clock:
            return []
        
        comparison = self.compare_clocks(current_clock, new_clock)
        conflicts = []
        
        if comparison == 'concurrent':
            conflicts.append({
                'type': 'concurrent_modification',
                'current_clock': current_clock,
                'new_clock': new_clock,
                'description': 'Concurrent modifications detected'
            })
        
        return conflicts
    
    def cleanup_old_clocks(self, max_age_hours: int = 24):
        """Очистить старые vector clocks"""
        # В реальной реализации здесь была бы логика очистки
        # старых clocks из базы данных
        pass

# Глобальный экземпляр менеджера vector clocks
vector_clock_manager = VectorClockManager()
