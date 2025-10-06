from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal


class LabeledDataCreate(BaseModel):
    session_id: str = Field(..., description="ID сессии")
    annotator_id: str = Field(..., description="ID разметчика")
    data_id: str = Field(..., description="ID данных")
    original_text: str = Field(..., description="Исходный текст")
    label: str = Field(..., description="Метка")
    confidence: Optional[Decimal] = Field(0.0, description="Уверенность в метке")
    vector_clock: Dict[str, int] = Field(..., description="Vector clock")


class LabeledDataUpdate(BaseModel):
    label: Optional[str] = Field(None, description="Новая метка")
    confidence: Optional[Decimal] = Field(None, description="Новая уверенность")
    vector_clock: Optional[Dict[str, int]] = Field(None, description="Обновленный vector clock")


class LabeledDataResponse(BaseModel):
    id: int = Field(..., description="ID записи")
    session_id: str = Field(..., description="ID сессии")
    annotator_id: str = Field(..., description="ID разметчика")
    data_id: str = Field(..., description="ID данных")
    original_text: str = Field(..., description="Исходный текст")
    label: str = Field(..., description="Метка")
    confidence: Decimal = Field(..., description="Уверенность в метке")
    vector_clock: Dict[str, int] = Field(..., description="Vector clock")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")
    is_conflict: bool = Field(..., description="Есть ли конфликт")
    conflict_resolution: str = Field(..., description="Разрешение конфликта")

    class Config:
        from_attributes = True


class ConflictResolution(BaseModel):
    conflict_id: int = Field(..., description="ID конфликта")
    resolution: str = Field(..., description="Тип разрешения")
    chosen_label: Optional[str] = Field(None, description="Выбранная метка")
    reason: Optional[str] = Field(None, description="Причина выбора")


class BatchLabelingRequest(BaseModel):
    session_id: str = Field(..., description="ID сессии")
    annotator_id: str = Field(..., description="ID разметчика")
    labels: List[Dict[str, Any]] = Field(..., description="Список меток для пакетной обработки")


class LabelingStats(BaseModel):
    total_labels: int = Field(..., description="Общее количество меток")
    conflicts: int = Field(..., description="Количество конфликтов")
    avg_confidence: float = Field(..., description="Средняя уверенность")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
