"""
Тесты для API эндпоинтов
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.privacy_policy import PrivacyPolicy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Создание тестовой базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAuthAPI:
    """Тесты для API аутентификации"""
    
    def test_login_success(self):
        """Тест успешного входа"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "password123"
        })
        
        # Проверка статуса ответа
        assert response.status_code == 200
        
        # Проверка наличия токена
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Тест входа с неверными учетными данными"""
        response = client.post("/api/v1/auth/login", json={
            "username": "invalid_user",
            "password": "invalid_password"
        })
        
        # Проверка статуса ответа
        assert response.status_code == 401
        
        # Проверка сообщения об ошибке
        data = response.json()
        assert "detail" in data
    
    def test_get_current_user_without_token(self):
        """Тест получения текущего пользователя без токена"""
        response = client.get("/api/v1/auth/me")
        
        # Проверка статуса ответа
        assert response.status_code == 401
    
    def test_get_current_user_with_invalid_token(self):
        """Тест получения текущего пользователя с неверным токеном"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # Проверка статуса ответа
        assert response.status_code == 401

class TestPrivacyAPI:
    """Тесты для API политик приватности"""
    
    def test_get_privacy_policies_without_auth(self):
        """Тест получения политик приватности без аутентификации"""
        response = client.get("/api/v1/privacy/policies")
        
        # Проверка статуса ответа
        assert response.status_code == 401
    
    def test_create_privacy_policy_without_auth(self):
        """Тест создания политики приватности без аутентификации"""
        response = client.post("/api/v1/privacy/policies", json={
            "name": "Test Policy",
            "description": "Test Description",
            "policy_type": "k_anonymity",
            "parameters": {"k": 5}
        })
        
        # Проверка статуса ответа
        assert response.status_code == 401

class TestQueryAPI:
    """Тесты для API запросов"""
    
    def test_execute_query_without_auth(self):
        """Тест выполнения запроса без аутентификации"""
        response = client.post("/api/v1/query/execute", json={
            "sql": "SELECT * FROM users LIMIT 1"
        })
        
        # Проверка статуса ответа
        assert response.status_code == 401
    
    def test_validate_query_without_auth(self):
        """Тест валидации запроса без аутентификации"""
        response = client.post("/api/v1/query/validate", json={
            "sql": "SELECT * FROM users LIMIT 1"
        })
        
        # Проверка статуса ответа
        assert response.status_code == 401

class TestAdminAPI:
    """Тесты для API администрирования"""
    
    def test_get_users_without_auth(self):
        """Тест получения пользователей без аутентификации"""
        response = client.get("/api/v1/admin/users")
        
        # Проверка статуса ответа
        assert response.status_code == 401
    
    def test_get_system_stats_without_auth(self):
        """Тест получения статистики системы без аутентификации"""
        response = client.get("/api/v1/admin/stats")
        
        # Проверка статуса ответа
        assert response.status_code == 401

class TestMonitoringAPI:
    """Тесты для API мониторинга"""
    
    def test_get_health_status(self):
        """Тест получения статуса здоровья"""
        response = client.get("/api/v1/monitoring/health")
        
        # Проверка статуса ответа
        assert response.status_code == 200
        
        # Проверка структуры ответа
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "redis" in data
    
    def test_get_metrics_without_auth(self):
        """Тест получения метрик без аутентификации"""
        response = client.get("/api/v1/monitoring/metrics")
        
        # Проверка статуса ответа
        assert response.status_code == 401

class TestRootEndpoints:
    """Тесты для корневых эндпоинтов"""
    
    def test_root_endpoint(self):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        
        # Проверка статуса ответа
        assert response.status_code == 200
        
        # Проверка структуры ответа
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """Тест проверки здоровья"""
        response = client.get("/health")
        
        # Проверка статуса ответа
        assert response.status_code == 200
        
        # Проверка структуры ответа
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "redis" in data

if __name__ == '__main__':
    pytest.main([__file__])
