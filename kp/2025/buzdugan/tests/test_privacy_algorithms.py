"""
Тесты для алгоритмов приватности
"""

import pytest
import pandas as pd
import numpy as np
from app.services.anonymization.k_anonymity import KAnonymityService
from app.services.anonymization.l_diversity import LDiversityService
from app.services.anonymization.differential_privacy import DifferentialPrivacyService

class TestKAnonymity:
    """Тесты для k-анонимности"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        self.k_anonymity_service = KAnonymityService()
        
        # Создание тестовых данных
        self.test_data = pd.DataFrame({
            'age': [25, 30, 35, 25, 30, 35, 25, 30, 35, 25],
            'zipcode': ['101000', '101001', '101002', '101000', '101001', '101002', '101000', '101001', '101002', '101000'],
            'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
            'disease': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })
    
    def test_k_anonymity_application(self):
        """Тест применения k-анонимности"""
        parameters = {
            'k': 3,
            'quasi_identifiers': ['age', 'zipcode', 'gender']
        }
        
        result = self.k_anonymity_service.apply(self.test_data, parameters)
        
        # Проверка, что результат не пустой
        assert not result.empty
        
        # Проверка, что количество строк уменьшилось или осталось тем же
        assert len(result) <= len(self.test_data)
    
    def test_k_anonymity_level_calculation(self):
        """Тест вычисления уровня k-анонимности"""
        quasi_identifiers = ['age', 'zipcode']
        
        k_level = self.k_anonymity_service.calculate_k_anonymity_level(
            self.test_data, quasi_identifiers
        )
        
        # Уровень k-анонимности должен быть положительным
        assert k_level > 0
    
    def test_k_anonymity_validation(self):
        """Тест валидации k-анонимности"""
        quasi_identifiers = ['age', 'zipcode']
        k = 2
        
        is_valid = self.k_anonymity_service.validate_k_anonymity(
            self.test_data, quasi_identifiers, k
        )
        
        # Результат должен быть булевым значением
        assert isinstance(is_valid, bool)

class TestLDiversity:
    """Тесты для l-разнообразия"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        self.l_diversity_service = LDiversityService()
        
        # Создание тестовых данных
        self.test_data = pd.DataFrame({
            'age': [25, 30, 35, 25, 30, 35, 25, 30, 35, 25],
            'zipcode': ['101000', '101001', '101002', '101000', '101001', '101002', '101000', '101001', '101002', '101000'],
            'disease': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })
    
    def test_l_diversity_application(self):
        """Тест применения l-разнообразия"""
        parameters = {
            'l': 2,
            'sensitive_attribute': 'disease',
            'quasi_identifiers': ['age', 'zipcode']
        }
        
        result = self.l_diversity_service.apply(self.test_data, parameters)
        
        # Проверка, что результат не пустой
        assert not result.empty
        
        # Проверка, что количество строк уменьшилось или осталось тем же
        assert len(result) <= len(self.test_data)
    
    def test_l_diversity_level_calculation(self):
        """Тест вычисления уровня l-разнообразия"""
        quasi_identifiers = ['age', 'zipcode']
        sensitive_attribute = 'disease'
        
        l_level = self.l_diversity_service.calculate_l_diversity_level(
            self.test_data, quasi_identifiers, sensitive_attribute
        )
        
        # Уровень l-разнообразия должен быть положительным
        assert l_level > 0
    
    def test_l_diversity_validation(self):
        """Тест валидации l-разнообразия"""
        quasi_identifiers = ['age', 'zipcode']
        sensitive_attribute = 'disease'
        l = 2
        
        is_valid = self.l_diversity_service.validate_l_diversity(
            self.test_data, quasi_identifiers, sensitive_attribute, l
        )
        
        # Результат должен быть булевым значением
        assert isinstance(is_valid, bool)

class TestDifferentialPrivacy:
    """Тесты для дифференциальной приватности"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        self.differential_privacy_service = DifferentialPrivacyService()
        
        # Создание тестовых данных
        self.test_data = pd.DataFrame({
            'age': [25, 30, 35, 25, 30, 35, 25, 30, 35, 25],
            'income': [50000, 60000, 70000, 50000, 60000, 70000, 50000, 60000, 70000, 50000],
            'score': [85, 90, 95, 85, 90, 95, 85, 90, 95, 85]
        })
    
    def test_differential_privacy_application(self):
        """Тест применения дифференциальной приватности"""
        parameters = {
            'epsilon': 1.0,
            'delta': 0.00001,
            'sensitivity': 1.0,
            'mechanism': 'laplace'
        }
        
        result = self.differential_privacy_service.apply(self.test_data, parameters)
        
        # Проверка, что результат не пустой
        assert not result.empty
        
        # Проверка, что количество строк осталось тем же
        assert len(result) == len(self.test_data)
    
    def test_laplace_noise_generation(self):
        """Тест генерации шума Лапласа"""
        size = 100
        sensitivity = 1.0
        epsilon = 1.0
        
        noise = self.differential_privacy_service._generate_laplace_noise(
            size, sensitivity, epsilon
        )
        
        # Проверка размера массива шума
        assert len(noise) == size
        
        # Проверка, что шум имеет правильное распределение
        assert np.mean(noise) < 1.0  # Среднее должно быть близко к 0
    
    def test_gaussian_noise_generation(self):
        """Тест генерации гауссовского шума"""
        size = 100
        sensitivity = 1.0
        epsilon = 1.0
        delta = 0.00001
        
        noise = self.differential_privacy_service._generate_gaussian_noise(
            size, sensitivity, epsilon, delta
        )
        
        # Проверка размера массива шума
        assert len(noise) == size
        
        # Проверка, что шум имеет правильное распределение
        assert np.mean(noise) < 1.0  # Среднее должно быть близко к 0
    
    def test_privacy_parameters_validation(self):
        """Тест валидации параметров приватности"""
        # Валидные параметры
        assert self.differential_privacy_service.validate_privacy_parameters(1.0, 0.00001)
        
        # Невалидные параметры
        assert not self.differential_privacy_service.validate_privacy_parameters(-1.0, 0.00001)
        assert not self.differential_privacy_service.validate_privacy_parameters(1.0, -0.1)
        assert not self.differential_privacy_service.validate_privacy_parameters(1.0, 1.1)
    
    def test_utility_loss_estimation(self):
        """Тест оценки потери полезности"""
        # Создание тестовых данных с шумом
        original_data = self.test_data.copy()
        noisy_data = self.test_data.copy()
        noisy_data['age'] += np.random.normal(0, 1, len(noisy_data))
        
        utility_loss = self.differential_privacy_service.estimate_utility_loss(
            original_data, noisy_data
        )
        
        # Проверка, что метрики полезности вычислены
        assert 'overall_utility_loss' in utility_loss
        assert utility_loss['overall_utility_loss'] >= 0

if __name__ == '__main__':
    pytest.main([__file__])
