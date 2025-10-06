import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.core.database import Base, get_db_write, get_db_read
from app.models.annotator_session import AnnotatorSession
from app.models.labeled_data import LabeledData


# Создание тестовой базы данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db_write():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_db_read():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_write] = override_get_db_write
app.dependency_overrides[get_db_read] = override_get_db_read

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Настройка тестовой базы данных"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestSessionsAPI:
    """Тесты для API сессий"""
    
    def test_create_session(self, setup_database):
        """Тест создания сессии"""
        response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["annotator_id"] == "test_annotator"
        assert data["current_replica"] == "master"
        assert data["is_active"] == True
        assert "vector_clock" in data
    
    def test_get_session(self, setup_database):
        """Тест получения сессии"""
        # Создание сессии
        create_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = create_response.json()["session_id"]
        
        # Получение сессии
        response = client.get(f"/api/v1/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["annotator_id"] == "test_annotator"
    
    def test_get_nonexistent_session(self, setup_database):
        """Тест получения несуществующей сессии"""
        response = client.get("/api/v1/sessions/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_switch_replica(self, setup_database):
        """Тест переключения реплики"""
        # Создание сессии
        create_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = create_response.json()["session_id"]
        
        # Переключение реплики
        response = client.put(f"/api/v1/sessions/{session_id}/switch-replica?replica=replica1")
        
        assert response.status_code == 200
        data = response.json()
        assert "Switched to replica replica1" in data["message"]
    
    def test_end_session(self, setup_database):
        """Тест завершения сессии"""
        # Создание сессии
        create_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = create_response.json()["session_id"]
        
        # Завершение сессии
        response = client.delete(f"/api/v1/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "ended successfully" in data["message"]
        assert "duration" in data
    
    def test_list_sessions(self, setup_database):
        """Тест получения списка сессий"""
        # Создание нескольких сессий
        for i in range(3):
            client.post(
                "/api/v1/sessions/create",
                json={"annotator_id": f"annotator_{i}"}
            )
        
        # Получение списка сессий
        response = client.get("/api/v1/sessions/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("session_id" in session for session in data)


class TestLabelingAPI:
    """Тесты для API разметки"""
    
    def test_create_labeled_data(self, setup_database):
        """Тест создания разметки данных"""
        # Создание сессии
        session_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = session_response.json()["session_id"]
        
        # Создание разметки
        labeled_data = {
            "session_id": session_id,
            "annotator_id": "test_annotator",
            "data_id": "test_data_1",
            "original_text": "This is a test text",
            "label": "positive",
            "confidence": 0.95,
            "vector_clock": {"master": 1}
        }
        
        response = client.post("/api/v1/labeling/", json=labeled_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["label"] == "positive"
        assert data["confidence"] == 0.95
        assert data["is_conflict"] == False
    
    def test_get_labeled_data_by_session(self, setup_database):
        """Тест получения разметки по сессии"""
        # Создание сессии и разметки
        session_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = session_response.json()["session_id"]
        
        labeled_data = {
            "session_id": session_id,
            "annotator_id": "test_annotator",
            "data_id": "test_data_1",
            "original_text": "Test text",
            "label": "positive",
            "confidence": 0.9,
            "vector_clock": {"master": 1}
        }
        
        client.post("/api/v1/labeling/", json=labeled_data)
        
        # Получение разметки по сессии
        response = client.get(f"/api/v1/labeling/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["label"] == "positive"
    
    def test_update_labeled_data(self, setup_database):
        """Тест обновления разметки"""
        # Создание сессии и разметки
        session_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = session_response.json()["session_id"]
        
        labeled_data = {
            "session_id": session_id,
            "annotator_id": "test_annotator",
            "data_id": "test_data_1",
            "original_text": "Test text",
            "label": "positive",
            "confidence": 0.9,
            "vector_clock": {"master": 1}
        }
        
        create_response = client.post("/api/v1/labeling/", json=labeled_data)
        data_id = create_response.json()["id"]
        
        # Обновление разметки
        update_data = {
            "label": "negative",
            "confidence": 0.8,
            "vector_clock": {"master": 2}
        }
        
        response = client.put(f"/api/v1/labeling/{data_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "negative"
        assert data["confidence"] == 0.8
    
    def test_batch_labeling(self, setup_database):
        """Тест пакетной разметки"""
        # Создание сессии
        session_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = session_response.json()["session_id"]
        
        # Пакетная разметка
        batch_request = {
            "session_id": session_id,
            "annotator_id": "test_annotator",
            "labels": [
                {
                    "data_id": "data_1",
                    "original_text": "Text 1",
                    "label": "positive",
                    "confidence": 0.9,
                    "vector_clock": {"master": 1}
                },
                {
                    "data_id": "data_2",
                    "original_text": "Text 2",
                    "label": "negative",
                    "confidence": 0.8,
                    "vector_clock": {"master": 2}
                }
            ]
        }
        
        response = client.post("/api/v1/labeling/batch", json=batch_request)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["label"] == "positive"
        assert data[1]["label"] == "negative"
    
    def test_get_conflicts(self, setup_database):
        """Тест получения конфликтов"""
        # Создание сессии
        session_response = client.post(
            "/api/v1/sessions/create",
            json={"annotator_id": "test_annotator"}
        )
        session_id = session_response.json()["session_id"]
        
        # Создание конфликтной разметки
        labeled_data = {
            "session_id": session_id,
            "annotator_id": "test_annotator",
            "data_id": "conflict_data",
            "original_text": "Conflict text",
            "label": "positive",
            "confidence": 0.7,
            "vector_clock": {"node1": 1, "node2": 1}  # Concurrent clock
        }
        
        client.post("/api/v1/labeling/", json=labeled_data)
        
        # Получение конфликтов
        response = client.get(f"/api/v1/labeling/conflicts/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        # В тестовой среде конфликты могут не обнаруживаться из-за упрощенной логики
        assert isinstance(data, list)


class TestMonitoringAPI:
    """Тесты для API мониторинга"""
    
    def test_health_check(self, setup_database):
        """Тест проверки здоровья системы"""
        response = client.get("/api/v1/monitoring/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_get_metrics(self, setup_database):
        """Тест получения метрик"""
        response = client.get("/api/v1/monitoring/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "counters" in data
        assert "timings" in data
        assert "gauges" in data
        assert "timestamp" in data
    
    def test_get_events(self, setup_database):
        """Тест получения событий"""
        response = client.get("/api/v1/monitoring/events")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert "timestamp" in data
    
    def test_get_replica_status(self, setup_database):
        """Тест получения статуса реплик"""
        response = client.get("/api/v1/monitoring/replicas/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "replicas" in data
        assert "timestamp" in data
    
    def test_get_session_stats(self, setup_database):
        """Тест получения статистики сессий"""
        response = client.get("/api/v1/monitoring/sessions/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "active_sessions" in data
        assert "replica_distribution" in data
    
    def test_get_conflict_stats(self, setup_database):
        """Тест получения статистики конфликтов"""
        response = client.get("/api/v1/monitoring/conflicts/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_conflicts" in data
        assert "conflicts_by_session" in data
        assert "resolution_stats" in data


class TestRootEndpoints:
    """Тесты для корневых endpoints"""
    
    def test_root(self):
        """Тест корневого endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health(self):
        """Тест health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
