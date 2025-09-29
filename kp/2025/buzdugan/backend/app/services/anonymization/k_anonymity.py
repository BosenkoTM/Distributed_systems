"""
Реализация алгоритма k-анонимности
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class KAnonymityService:
    """Сервис для применения k-анонимности"""
    
    def __init__(self):
        self.logger = logger
    
    async def apply(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Применение k-анонимности к данным
        
        Args:
            data: Исходные данные
            parameters: Параметры k-анонимности
                - k: минимальное количество записей в группе
                - quasi_identifiers: список квази-идентификаторов
        
        Returns:
            Анонимизированные данные
        """
        try:
            k = parameters.get("k", 5)
            quasi_identifiers = parameters.get("quasi_identifiers", [])
            
            if not quasi_identifiers:
                self.logger.warning("Не указаны квази-идентификаторы для k-анонимности")
                return data
            
            # Проверка наличия квази-идентификаторов в данных
            available_qi = [col for col in quasi_identifiers if col in data.columns]
            if not available_qi:
                self.logger.warning("Квази-идентификаторы не найдены в данных")
                return data
            
            # Применение k-анонимности
            anonymized_data = await self._apply_k_anonymity(data, available_qi, k)
            
            self.logger.info("Применена k-анонимность",
                           k=k,
                           quasi_identifiers=available_qi,
                           original_rows=len(data),
                           anonymized_rows=len(anonymized_data))
            
            return anonymized_data
            
        except Exception as e:
            self.logger.error(f"Ошибка применения k-анонимности: {e}")
            return data
    
    async def _apply_k_anonymity(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str], 
        k: int
    ) -> pd.DataFrame:
        """Применение алгоритма k-анонимности"""
        try:
            # Создание копии данных
            anonymized_data = data.copy()
            
            # Группировка по квази-идентификаторам
            groups = anonymized_data.groupby(quasi_identifiers)
            
            # Фильтрация групп с размером >= k
            valid_groups = []
            for name, group in groups:
                if len(group) >= k:
                    valid_groups.append(group)
                else:
                    # Для групп с размером < k применяем обобщение
                    generalized_group = await self._generalize_group(group, quasi_identifiers)
                    if len(generalized_group) >= k:
                        valid_groups.append(generalized_group)
            
            if not valid_groups:
                self.logger.warning("Не удалось создать группы с k-анонимностью")
                return data
            
            # Объединение валидных групп
            result = pd.concat(valid_groups, ignore_index=True)
            
            # Применение обобщения к квази-идентификаторам
            for qi in quasi_identifiers:
                if qi in result.columns:
                    result[qi] = await self._generalize_column(result[qi])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка применения алгоритма k-анонимности: {e}")
            return data
    
    async def _generalize_group(
        self, 
        group: pd.DataFrame, 
        quasi_identifiers: List[str]
    ) -> pd.DataFrame:
        """Обобщение группы для достижения k-анонимности"""
        try:
            generalized_group = group.copy()
            
            for qi in quasi_identifiers:
                if qi in generalized_group.columns:
                    # Применение обобщения к колонке
                    generalized_group[qi] = await self._generalize_column(generalized_group[qi])
            
            return generalized_group
            
        except Exception as e:
            self.logger.error(f"Ошибка обобщения группы: {e}")
            return group
    
    async def _generalize_column(self, column: pd.Series) -> pd.Series:
        """Обобщение значений в колонке"""
        try:
            if column.dtype == 'object':
                # Для строковых данных - обрезание до первых символов
                return column.astype(str).str[:3] + "***"
            
            elif pd.api.types.is_numeric_dtype(column):
                # Для числовых данных - округление до ближайшего десятка
                return (column / 10).round() * 10
            
            elif pd.api.types.is_datetime64_any_dtype(column):
                # Для дат - округление до года
                return column.dt.year
            
            else:
                # Для других типов - возврат без изменений
                return column
                
        except Exception as e:
            self.logger.error(f"Ошибка обобщения колонки: {e}")
            return column
    
    async def calculate_k_anonymity_level(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str]
    ) -> int:
        """Вычисление уровня k-анонимности данных"""
        try:
            if not quasi_identifiers:
                return 0
            
            # Группировка по квази-идентификаторам
            groups = data.groupby(quasi_identifiers)
            
            # Поиск минимального размера группы
            min_group_size = min(len(group) for _, group in groups)
            
            return min_group_size
            
        except Exception as e:
            self.logger.error(f"Ошибка вычисления уровня k-анонимности: {e}")
            return 0
    
    async def validate_k_anonymity(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str], 
        k: int
    ) -> bool:
        """Проверка соответствия данных требованиям k-анонимности"""
        try:
            actual_k = await self.calculate_k_anonymity_level(data, quasi_identifiers)
            return actual_k >= k
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации k-анонимности: {e}")
            return False
