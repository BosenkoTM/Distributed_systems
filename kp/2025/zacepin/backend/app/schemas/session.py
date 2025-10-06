from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class SessionCreate(BaseModel):
    annotator_id: str = Field(..., description="ID разметчика")
    initial_replica: Optional[str] = Field("master", description="Начальная реплика")


class SessionUpdate(BaseModel):
    current_replica: Optional[str] = Field(None, description="Текущая реплика")
    is_active: Optional[bool] = Field(None, description="Активность сессии")


class SessionResponse(BaseModel):
    session_id: str = Field(..., description="ID сессии")
    annotator_id: str = Field(..., description="ID разметчика")
    current_replica: str = Field(..., description="Текущая реплика")
    is_active: bool = Field(..., description="Активность сессии")
    vector_clock: Dict[str, int] = Field(..., description="Vector clock")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    created_at: Optional[datetime] = Field(None, description="Время создания")

    class Config:
        from_attributes = True
