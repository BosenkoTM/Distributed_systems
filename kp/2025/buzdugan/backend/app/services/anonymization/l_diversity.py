"""
Реализация алгоритма l-разнообразия
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class LDiversityService:
    """Сервис для применения l-разнообразия"""
    
    def __init__(self):
        self.logger = logger
    
    async def apply(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """
        Применение l-разнообразия к данным
        
        Args:
            data: Исходные данные
            parameters: Параметры l-разнообразия
                - l: минимальное количество различных значений чувствительного атрибута
                - sensitive_attribute: чувствительный атрибут
                - quasi_identifiers: список квази-идентификаторов
        
        Returns:
            Анонимизированные данные
        """
        try:
            l = parameters.get("l", 3)
            sensitive_attribute = parameters.get("sensitive_attribute")
            quasi_identifiers = parameters.get("quasi_identifiers", [])
            
            if not sensitive_attribute:
                self.logger.warning("Не указан чувствительный атрибут для l-разнообразия")
                return data
            
            if sensitive_attribute not in data.columns:
                self.logger.warning(f"Чувствительный атрибут '{sensitive_attribute}' не найден в данных")
                return data
            
            if not quasi_identifiers:
                self.logger.warning("Не указаны квази-идентификаторы для l-разнообразия")
                return data
            
            # Проверка наличия квази-идентификаторов в данных
            available_qi = [col for col in quasi_identifiers if col in data.columns]
            if not available_qi:
                self.logger.warning("Квази-идентификаторы не найдены в данных")
                return data
            
            # Применение l-разнообразия
            anonymized_data = await self._apply_l_diversity(
                data, available_qi, sensitive_attribute, l
            )
            
            self.logger.info("Применено l-разнообразие",
                           l=l,
                           sensitive_attribute=sensitive_attribute,
                           quasi_identifiers=available_qi,
                           original_rows=len(data),
                           anonymized_rows=len(anonymized_data))
            
            return anonymized_data
            
        except Exception as e:
            self.logger.error(f"Ошибка применения l-разнообразия: {e}")
            return data
    
    async def _apply_l_diversity(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str], 
        sensitive_attribute: str, 
        l: int
    ) -> pd.DataFrame:
        """Применение алгоритма l-разнообразия"""
        try:
            # Создание копии данных
            anonymized_data = data.copy()
            
            # Группировка по квази-идентификаторам
            groups = anonymized_data.groupby(quasi_identifiers)
            
            # Фильтрация групп с l-разнообразием
            valid_groups = []
            for name, group in groups:
                # Подсчет уникальных значений чувствительного атрибута
                unique_sensitive_values = group[sensitive_attribute].nunique()
                
                if unique_sensitive_values >= l:
                    valid_groups.append(group)
                else:
                    # Для групп без l-разнообразия применяем обобщение
                    generalized_group = await self._generalize_for_l_diversity(
                        group, quasi_identifiers, sensitive_attribute, l
                    )
                    if generalized_group is not None:
                        valid_groups.append(generalized_group)
            
            if not valid_groups:
                self.logger.warning("Не удалось создать группы с l-разнообразием")
                return data
            
            # Объединение валидных групп
            result = pd.concat(valid_groups, ignore_index=True)
            
            # Применение обобщения к квази-идентификаторам
            for qi in quasi_identifiers:
                if qi in result.columns:
                    result[qi] = await self._generalize_column(result[qi])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка применения алгоритма l-разнообразия: {e}")
            return data
    
    async def _generalize_for_l_diversity(
        self, 
        group: pd.DataFrame, 
        quasi_identifiers: List[str], 
        sensitive_attribute: str, 
        l: int
    ) -> pd.DataFrame:
        """Обобщение группы для достижения l-разнообразия"""
        try:
            generalized_group = group.copy()
            
            # Применение обобщения к квази-идентификаторам
            for qi in quasi_identifiers:
                if qi in generalized_group.columns:
                    generalized_group[qi] = await self._generalize_column(generalized_group[qi])
            
            # Проверка l-разнообразия после обобщения
            unique_sensitive_values = generalized_group[sensitive_attribute].nunique()
            
            if unique_sensitive_values >= l:
                return generalized_group
            else:
                # Если l-разнообразие не достигнуто, возвращаем None
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка обобщения группы для l-разнообразия: {e}")
            return None
    
    async def _generalize_column(self, column: pd.Series) -> pd.Series:
        """Обобщение значений в колонке"""
        try:
            if column.dtype == 'object':
                # Для строковых данных - обрезание до первых символов
                return column.astype(str).str[:2] + "**"
            
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
    
    async def calculate_l_diversity_level(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str], 
        sensitive_attribute: str
    ) -> int:
        """Вычисление уровня l-разнообразия данных"""
        try:
            if not quasi_identifiers or sensitive_attribute not in data.columns:
                return 0
            
            # Группировка по квази-идентификаторам
            groups = data.groupby(quasi_identifiers)
            
            # Поиск минимального количества уникальных значений чувствительного атрибута
            min_diversity = min(
                group[sensitive_attribute].nunique() 
                for _, group in groups
            )
            
            return min_diversity
            
        except Exception as e:
            self.logger.error(f"Ошибка вычисления уровня l-разнообразия: {e}")
            return 0
    
    async def validate_l_diversity(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str], 
        sensitive_attribute: str, 
        l: int
    ) -> bool:
        """Проверка соответствия данных требованиям l-разнообразия"""
        try:
            actual_l = await self.calculate_l_diversity_level(
                data, quasi_identifiers, sensitive_attribute
            )
            return actual_l >= l
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации l-разнообразия: {e}")
            return False
    
    async def get_sensitive_attribute_distribution(
        self, 
        data: pd.DataFrame, 
        quasi_identifiers: List[str], 
        sensitive_attribute: str
    ) -> Dict[str, Any]:
        """Получение распределения чувствительного атрибута по группам"""
        try:
            if not quasi_identifiers or sensitive_attribute not in data.columns:
                return {}
            
            # Группировка по квази-идентификаторам
            groups = data.groupby(quasi_identifiers)
            
            distribution = {}
            for name, group in groups:
                group_key = str(name)
                distribution[group_key] = {
                    "size": len(group),
                    "unique_sensitive_values": group[sensitive_attribute].nunique(),
                    "sensitive_value_counts": group[sensitive_attribute].value_counts().to_dict()
                }
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Ошибка получения распределения чувствительного атрибута: {e}")
            return {}
