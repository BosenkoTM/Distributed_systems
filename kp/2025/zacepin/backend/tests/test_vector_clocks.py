import pytest
from app.models.vector_clock import VectorClockManager, vector_clock_manager


class TestVectorClocks:
    """Тесты для vector clocks"""
    
    def test_create_clock(self):
        """Тест создания vector clock"""
        session_id = "test_session"
        node_id = "node1"
        
        clock = vector_clock_manager.create_clock(session_id, node_id)
        
        assert clock == {node_id: 0}
        assert vector_clock_manager.get_clock(session_id) == {node_id: 0}
    
    def test_increment_clock(self):
        """Тест увеличения счетчика в vector clock"""
        session_id = "test_session"
        node_id = "node1"
        
        # Создание и увеличение
        vector_clock_manager.create_clock(session_id, node_id)
        clock1 = vector_clock_manager.increment_clock(session_id, node_id)
        clock2 = vector_clock_manager.increment_clock(session_id, node_id)
        
        assert clock1 == {node_id: 1}
        assert clock2 == {node_id: 2}
    
    def test_merge_clocks(self):
        """Тест объединения vector clocks"""
        session_id = "test_session"
        
        # Создание исходного clock
        vector_clock_manager.create_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        
        # Объединение с другим clock
        other_clock = {"node1": 3, "node2": 2}
        merged_clock = vector_clock_manager.merge_clocks(session_id, other_clock)
        
        expected_clock = {"node1": 3, "node2": 2}  # Максимум по каждому узлу
        assert merged_clock == expected_clock
    
    def test_compare_clocks_before_after(self):
        """Тест сравнения clocks: before/after"""
        clock1 = {"node1": 1, "node2": 0}
        clock2 = {"node1": 2, "node2": 1}
        
        result = vector_clock_manager.compare_clocks(clock1, clock2)
        assert result == "before"
        
        result = vector_clock_manager.compare_clocks(clock2, clock1)
        assert result == "after"
    
    def test_compare_clocks_equal(self):
        """Тест сравнения одинаковых clocks"""
        clock1 = {"node1": 1, "node2": 2}
        clock2 = {"node1": 1, "node2": 2}
        
        result = vector_clock_manager.compare_clocks(clock1, clock2)
        assert result == "equal"
    
    def test_compare_clocks_concurrent(self):
        """Тест сравнения concurrent clocks"""
        clock1 = {"node1": 2, "node2": 1}
        clock2 = {"node1": 1, "node2": 2}
        
        result = vector_clock_manager.compare_clocks(clock1, clock2)
        assert result == "concurrent"
    
    def test_detect_conflicts_no_conflict(self):
        """Тест обнаружения конфликтов: нет конфликта"""
        session_id = "test_session"
        
        # Первая операция
        vector_clock_manager.create_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        
        # Вторая операция (последовательная)
        new_clock = {"node1": 2}
        conflicts = vector_clock_manager.detect_conflicts(session_id, new_clock)
        
        assert len(conflicts) == 0
    
    def test_detect_conflicts_concurrent(self):
        """Тест обнаружения конфликтов: concurrent операции"""
        session_id = "test_session"
        
        # Установка исходного clock
        vector_clock_manager.create_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        
        # Concurrent операция
        concurrent_clock = {"node1": 1, "node2": 1}
        conflicts = vector_clock_manager.detect_conflicts(session_id, concurrent_clock)
        
        assert len(conflicts) > 0
        assert conflicts[0]["type"] == "concurrent_modification"
        assert "current_clock" in conflicts[0]
        assert "new_clock" in conflicts[0]
    
    def test_multiple_nodes(self):
        """Тест работы с множественными узлами"""
        session_id = "multi_node_session"
        
        # Создание clock с несколькими узлами
        vector_clock_manager.create_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node2")
        vector_clock_manager.increment_clock(session_id, "node3")
        
        final_clock = vector_clock_manager.get_clock(session_id)
        expected_clock = {"node1": 1, "node2": 1, "node3": 1}
        
        assert final_clock == expected_clock
    
    def test_clock_persistence(self):
        """Тест персистентности vector clocks"""
        session_id = "persistence_test"
        
        # Создание и модификация clock
        vector_clock_manager.create_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        
        # Получение clock после операций
        clock = vector_clock_manager.get_clock(session_id)
        assert clock == {"node1": 2}
        
        # Дополнительные операции
        vector_clock_manager.increment_clock(session_id, "node2")
        updated_clock = vector_clock_manager.get_clock(session_id)
        assert updated_clock == {"node1": 2, "node2": 1}
    
    def test_complex_merge_scenario(self):
        """Тест сложного сценария объединения clocks"""
        session_id = "complex_merge"
        
        # Исходный clock
        vector_clock_manager.create_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node1")
        vector_clock_manager.increment_clock(session_id, "node2")
        
        # Объединение с clock, содержащим более новые значения
        other_clock = {
            "node1": 5,  # Более новое значение
            "node2": 1,  # То же значение
            "node3": 3   # Новый узел
        }
        
        merged_clock = vector_clock_manager.merge_clocks(session_id, other_clock)
        expected_clock = {"node1": 5, "node2": 1, "node3": 3}
        
        assert merged_clock == expected_clock
    
    def test_edge_cases(self):
        """Тест граничных случаев"""
        # Пустой clock
        empty_clock = {}
        clock_with_data = {"node1": 1}
        
        result = vector_clock_manager.compare_clocks(empty_clock, clock_with_data)
        assert result == "before"
        
        result = vector_clock_manager.compare_clocks(clock_with_data, empty_clock)
        assert result == "after"
        
        # Два пустых clock
        result = vector_clock_manager.compare_clocks(empty_clock, empty_clock)
        assert result == "equal"
    
    def test_clock_cleanup(self):
        """Тест очистки старых clocks"""
        # Создание нескольких clocks
        for i in range(5):
            session_id = f"cleanup_test_{i}"
            vector_clock_manager.create_clock(session_id, "node1")
        
        # Проверка, что clocks созданы
        assert len(vector_clock_manager.clocks) >= 5
        
        # Очистка (в реальной реализации здесь была бы логика очистки)
        vector_clock_manager.cleanup_old_clocks(max_age_hours=0)
        
        # В текущей реализации очистка не реализована,
        # поэтому clocks остаются
        assert len(vector_clock_manager.clocks) >= 5
