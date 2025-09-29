"""
Реализация дифференциальной приватности
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import structlog
import math

logger = structlog.get_logger(__name__)

class DifferentialPrivacyService:
    """Сервис для применения дифференциальной приватности"""
    
    def __init__(self):
        self.logger = logger
    
    async def apply(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Применение дифференциальной приватности к данным
        
        Args:
            data: Исходные данные
            parameters: Параметры дифференциальной приватности
                - epsilon: параметр приватности (меньше = больше приватности)
                - delta: параметр вероятности утечки
                - sensitivity: чувствительность функции
                - mechanism: механизм добавления шума ('laplace', 'gaussian')
        
        Returns:
            Анонимизированные данные
        """
        try:
            epsilon = parameters.get("epsilon", 1.0)
            delta = parameters.get("delta", 0.00001)
            sensitivity = parameters.get("sensitivity", 1.0)
            mechanism = parameters.get("mechanism", "laplace")
            
            if epsilon <= 0:
                self.logger.warning("Epsilon должен быть положительным")
                return data
            
            # Применение дифференциальной приватности
            anonymized_data = await self._apply_differential_privacy(
                data, epsilon, delta, sensitivity, mechanism
            )
            
            self.logger.info("Применена дифференциальная приватность",
                           epsilon=epsilon,
                           delta=delta,
                           sensitivity=sensitivity,
                           mechanism=mechanism,
                           original_rows=len(data),
                           anonymized_rows=len(anonymized_data))
            
            return anonymized_data
            
        except Exception as e:
            self.logger.error(f"Ошибка применения дифференциальной приватности: {e}")
            return data
    
    async def _apply_differential_privacy(
        self, 
        data: pd.DataFrame, 
        epsilon: float, 
        delta: float, 
        sensitivity: float, 
        mechanism: str
    ) -> pd.DataFrame:
        """Применение алгоритма дифференциальной приватности"""
        try:
            # Создание копии данных
            anonymized_data = data.copy()
            
            # Применение шума к числовым колонкам
            for column in anonymized_data.columns:
                if pd.api.types.is_numeric_dtype(anonymized_data[column]):
                    if mechanism == "laplace":
                        noise = await self._generate_laplace_noise(
                            len(anonymized_data), sensitivity, epsilon
                        )
                    elif mechanism == "gaussian":
                        noise = await self._generate_gaussian_noise(
                            len(anonymized_data), sensitivity, epsilon, delta
                        )
                    else:
                        self.logger.warning(f"Неизвестный механизм: {mechanism}")
                        continue
                    
                    anonymized_data[column] = anonymized_data[column] + noise
            
            return anonymized_data
            
        except Exception as e:
            self.logger.error(f"Ошибка применения алгоритма дифференциальной приватности: {e}")
            return data
    
    async def _generate_laplace_noise(
        self, 
        size: int, 
        sensitivity: float, 
        epsilon: float
    ) -> np.ndarray:
        """Генерация шума Лапласа"""
        try:
            # Параметр масштаба для распределения Лапласа
            scale = sensitivity / epsilon
            
            # Генерация шума
            noise = np.random.laplace(0, scale, size)
            
            return noise
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации шума Лапласа: {e}")
            return np.zeros(size)
    
    async def _generate_gaussian_noise(
        self, 
        size: int, 
        sensitivity: float, 
        epsilon: float, 
        delta: float
    ) -> np.ndarray:
        """Генерация гауссовского шума"""
        try:
            # Параметр масштаба для гауссовского распределения
            sigma = math.sqrt(2 * math.log(1.25 / delta)) * sensitivity / epsilon
            
            # Генерация шума
            noise = np.random.normal(0, sigma, size)
            
            return noise
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации гауссовского шума: {e}")
            return np.zeros(size)
    
    async def apply_to_aggregate(
        self, 
        aggregate_value: float, 
        parameters: Dict[str, Any]
    ) -> float:
        """Применение дифференциальной приватности к агрегированному значению"""
        try:
            epsilon = parameters.get("epsilon", 1.0)
            delta = parameters.get("delta", 0.00001)
            sensitivity = parameters.get("sensitivity", 1.0)
            mechanism = parameters.get("mechanism", "laplace")
            
            if mechanism == "laplace":
                noise = await self._generate_laplace_noise(1, sensitivity, epsilon)[0]
            elif mechanism == "gaussian":
                noise = await self._generate_gaussian_noise(1, sensitivity, epsilon, delta)[0]
            else:
                self.logger.warning(f"Неизвестный механизм: {mechanism}")
                return aggregate_value
            
            return aggregate_value + noise
            
        except Exception as e:
            self.logger.error(f"Ошибка применения дифференциальной приватности к агрегату: {e}")
            return aggregate_value
    
    async def calculate_privacy_budget(
        self, 
        queries: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Вычисление бюджета приватности для набора запросов"""
        try:
            total_epsilon = 0
            total_delta = 0
            
            for query in queries:
                total_epsilon += query.get("epsilon", 0)
                total_delta += query.get("delta", 0)
            
            return {
                "total_epsilon": total_epsilon,
                "total_delta": total_delta,
                "remaining_epsilon": max(0, 1.0 - total_epsilon),
                "remaining_delta": max(0, 0.00001 - total_delta)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка вычисления бюджета приватности: {e}")
            return {}
    
    async def validate_privacy_parameters(
        self, 
        epsilon: float, 
        delta: float
    ) -> bool:
        """Валидация параметров приватности"""
        try:
            # Epsilon должен быть положительным
            if epsilon <= 0:
                return False
            
            # Delta должен быть в диапазоне [0, 1]
            if delta < 0 or delta > 1:
                return False
            
            # Для практических применений delta должен быть очень маленьким
            if delta > 0.01:
                self.logger.warning("Delta слишком большой для практического применения")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации параметров приватности: {e}")
            return False
    
    async def estimate_utility_loss(
        self, 
        original_data: pd.DataFrame, 
        anonymized_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Оценка потери полезности данных"""
        try:
            utility_metrics = {}
            
            # Вычисление метрик для числовых колонок
            numeric_columns = original_data.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                if column in anonymized_data.columns:
                    # Среднеквадратичная ошибка
                    mse = np.mean((original_data[column] - anonymized_data[column]) ** 2)
                    utility_metrics[f"{column}_mse"] = mse
                    
                    # Относительная ошибка
                    if np.mean(original_data[column]) != 0:
                        relative_error = mse / np.mean(original_data[column]) ** 2
                        utility_metrics[f"{column}_relative_error"] = relative_error
            
            # Общая метрика полезности
            if utility_metrics:
                utility_metrics["overall_utility_loss"] = np.mean(list(utility_metrics.values()))
            
            return utility_metrics
            
        except Exception as e:
            self.logger.error(f"Ошибка оценки потери полезности: {e}")
            return {}
