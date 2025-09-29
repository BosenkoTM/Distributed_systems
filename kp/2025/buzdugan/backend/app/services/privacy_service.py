"""
Сервис для работы с политиками приватности и анонимизацией данных
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import structlog
import asyncio

from app.models.privacy_policy import PrivacyPolicy
from app.models.user import User
from app.services.anonymization.k_anonymity import KAnonymityService
from app.services.anonymization.l_diversity import LDiversityService
from app.services.anonymization.differential_privacy import DifferentialPrivacyService

logger = structlog.get_logger(__name__)

class PrivacyService:
    def __init__(self, db: Session):
        self.db = db
        self.k_anonymity_service = KAnonymityService()
        self.l_diversity_service = LDiversityService()
        self.differential_privacy_service = DifferentialPrivacyService()
    
    async def get_all_policies(self) -> List[PrivacyPolicy]:
        """Получение всех политик приватности"""
        try:
            policies = self.db.query(PrivacyPolicy).filter(
                PrivacyPolicy.is_active == True
            ).all()
            
            logger.info("Получены политики приватности", count=len(policies))
            return policies
            
        except Exception as e:
            logger.error(f"Ошибка получения политик приватности: {e}")
            return []
    
    async def get_policy_by_id(self, policy_id: str) -> Optional[PrivacyPolicy]:
        """Получение политики по ID"""
        try:
            policy = self.db.query(PrivacyPolicy).filter(
                PrivacyPolicy.id == policy_id,
                PrivacyPolicy.is_active == True
            ).first()
            
            if policy:
                logger.info("Получена политика приватности", policy_id=policy_id)
            else:
                logger.warning("Политика приватности не найдена", policy_id=policy_id)
            
            return policy
            
        except Exception as e:
            logger.error(f"Ошибка получения политики приватности: {e}")
            return None
    
    async def create_policy(
        self,
        name: str,
        description: str,
        policy_type: str,
        parameters: Dict[str, Any],
        created_by: str
    ) -> PrivacyPolicy:
        """Создание новой политики приватности"""
        try:
            policy = PrivacyPolicy(
                name=name,
                description=description,
                policy_type=policy_type,
                parameters=parameters,
                created_by=created_by
            )
            
            self.db.add(policy)
            self.db.commit()
            self.db.refresh(policy)
            
            logger.info("Создана политика приватности", 
                       policy_id=str(policy.id),
                       name=name,
                       type=policy_type)
            
            return policy
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания политики приватности: {e}")
            raise
    
    async def update_policy(
        self,
        policy_id: str,
        **kwargs
    ) -> Optional[PrivacyPolicy]:
        """Обновление политики приватности"""
        try:
            policy = self.db.query(PrivacyPolicy).filter(
                PrivacyPolicy.id == policy_id
            ).first()
            
            if not policy:
                return None
            
            for key, value in kwargs.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            self.db.commit()
            self.db.refresh(policy)
            
            logger.info("Обновлена политика приватности", policy_id=policy_id)
            return policy
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обновления политики приватности: {e}")
            raise
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Удаление политики приватности"""
        try:
            policy = self.db.query(PrivacyPolicy).filter(
                PrivacyPolicy.id == policy_id
            ).first()
            
            if not policy:
                return False
            
            # Мягкое удаление - деактивация
            policy.is_active = False
            self.db.commit()
            
            logger.info("Удалена политика приватности", policy_id=policy_id)
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка удаления политики приватности: {e}")
            return False
    
    async def apply_anonymization(
        self,
        table_name: str,
        query: str,
        policy: PrivacyPolicy,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Применение анонимизации данных согласно политике"""
        try:
            # Получение данных из базы
            data = await self._execute_query(query)
            
            if data.empty:
                return {
                    "data": [],
                    "metrics": {"rows_processed": 0}
                }
            
            # Применение соответствующего алгоритма анонимизации
            if policy.policy_type == "k_anonymity":
                anonymized_data = await self.k_anonymity_service.apply(
                    data, policy.parameters
                )
            elif policy.policy_type == "l_diversity":
                anonymized_data = await self.l_diversity_service.apply(
                    data, policy.parameters
                )
            elif policy.policy_type == "differential_privacy":
                anonymized_data = await self.differential_privacy_service.apply(
                    data, policy.parameters
                )
            else:
                raise ValueError(f"Неподдерживаемый тип политики: {policy.policy_type}")
            
            # Вычисление метрик приватности
            metrics = await self._calculate_privacy_metrics(
                data, anonymized_data, policy
            )
            
            logger.info("Применена анонимизация данных",
                       policy_type=policy.policy_type,
                       table_name=table_name,
                       original_rows=len(data),
                       anonymized_rows=len(anonymized_data))
            
            return {
                "data": anonymized_data.to_dict('records'),
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Ошибка применения анонимизации: {e}")
            raise
    
    async def analyze_privacy_risks(
        self,
        query: str,
        tables_accessed: List[str]
    ) -> List[str]:
        """Анализ рисков приватности для запроса"""
        risks = []
        
        try:
            # Проверка на чувствительные поля
            sensitive_fields = ["name", "email", "phone", "address", "ssn", "passport"]
            query_lower = query.lower()
            
            for field in sensitive_fields:
                if field in query_lower:
                    risks.append(f"Запрос содержит чувствительное поле: {field}")
            
            # Проверка на агрегирующие функции
            if any(func in query_lower for func in ["count", "sum", "avg", "min", "max"]):
                risks.append("Запрос содержит агрегирующие функции")
            
            # Проверка на JOIN операции
            if "join" in query_lower:
                risks.append("Запрос содержит JOIN операции, что может привести к деанонимизации")
            
            # Проверка на подзапросы
            if "select" in query_lower and query_lower.count("select") > 1:
                risks.append("Запрос содержит подзапросы")
            
            logger.info("Проанализированы риски приватности", 
                       risks_count=len(risks),
                       tables=tables_accessed)
            
        except Exception as e:
            logger.error(f"Ошибка анализа рисков приватности: {e}")
        
        return risks
    
    async def generate_recommendations(
        self,
        query: str,
        privacy_risks: List[str]
    ) -> List[str]:
        """Генерация рекомендаций по улучшению приватности"""
        recommendations = []
        
        try:
            if not privacy_risks:
                recommendations.append("Запрос не содержит очевидных рисков приватности")
                return recommendations
            
            # Рекомендации на основе выявленных рисков
            for risk in privacy_risks:
                if "чувствительное поле" in risk:
                    recommendations.append("Рассмотрите применение k-анонимности для защиты персональных данных")
                elif "агрегирующие функции" in risk:
                    recommendations.append("Примените дифференциальную приватность для агрегирующих запросов")
                elif "JOIN операции" in risk:
                    recommendations.append("Ограничьте количество JOIN операций или примените l-разнообразие")
                elif "подзапросы" in risk:
                    recommendations.append("Упростите запрос, избегая сложных подзапросов")
            
            # Общие рекомендации
            recommendations.extend([
                "Регулярно пересматривайте политики приватности",
                "Мониторьте доступ к чувствительным данным",
                "Используйте принцип минимальных привилегий"
            ])
            
            logger.info("Сгенерированы рекомендации по приватности", 
                       recommendations_count=len(recommendations))
            
        except Exception as e:
            logger.error(f"Ошибка генерации рекомендаций: {e}")
        
        return recommendations
    
    async def get_privacy_metrics(self) -> Dict[str, Any]:
        """Получение метрик приватности"""
        try:
            # Подсчет политик по типам
            policy_counts = self.db.query(
                PrivacyPolicy.policy_type,
                self.db.func.count(PrivacyPolicy.id)
            ).filter(
                PrivacyPolicy.is_active == True
            ).group_by(PrivacyPolicy.policy_type).all()
            
            metrics = {
                "total_policies": sum(count for _, count in policy_counts),
                "policies_by_type": {policy_type: count for policy_type, count in policy_counts},
                "active_policies": len(await self.get_all_policies())
            }
            
            logger.info("Получены метрики приватности")
            return metrics
            
        except Exception as e:
            logger.error(f"Ошибка получения метрик приватности: {e}")
            return {}
    
    async def _execute_query(self, query: str) -> pd.DataFrame:
        """Выполнение SQL запроса и возврат данных в виде DataFrame"""
        try:
            # Здесь должна быть логика выполнения SQL запроса
            # Для демонстрации возвращаем пустой DataFrame
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            return pd.DataFrame()
    
    async def _calculate_privacy_metrics(
        self,
        original_data: pd.DataFrame,
        anonymized_data: pd.DataFrame,
        policy: PrivacyPolicy
    ) -> Dict[str, Any]:
        """Вычисление метрик приватности"""
        try:
            metrics = {
                "original_rows": len(original_data),
                "anonymized_rows": len(anonymized_data),
                "policy_type": policy.policy_type,
                "policy_name": policy.name
            }
            
            # Дополнительные метрики в зависимости от типа политики
            if policy.policy_type == "k_anonymity":
                k_value = policy.parameters.get("k", 0)
                metrics["k_value"] = k_value
                metrics["anonymization_ratio"] = len(anonymized_data) / len(original_data) if len(original_data) > 0 else 0
            
            elif policy.policy_type == "l_diversity":
                l_value = policy.parameters.get("l", 0)
                metrics["l_value"] = l_value
            
            elif policy.policy_type == "differential_privacy":
                epsilon = policy.parameters.get("epsilon", 0)
                delta = policy.parameters.get("delta", 0)
                metrics["epsilon"] = epsilon
                metrics["delta"] = delta
            
            return metrics
            
        except Exception as e:
            logger.error(f"Ошибка вычисления метрик приватности: {e}")
            return {}
