from datetime import datetime

from indicators.models import IndicatorStatus
from pydantic import BaseModel, ConfigDict, Field


class IndicatorBase(BaseModel):
    name: str = Field(..., description="Nome do indicador")
    sector: str = Field(..., description="Setor relacionado, ex: Hospedagem")
    period: str = Field(..., description="Período de referência, ex: 2026")
    value: float = Field(..., description="Valor numérico do indicador")
    unit: str = Field(..., description="Unidade de medida, ex: % ou R$")

class IndicatorCreate(IndicatorBase):
    status: IndicatorStatus | None = IndicatorStatus.DRAFT

class IndicatorUpdate(BaseModel):
    name: str | None = None
    sector: str | None = None
    period: str | None = None
    value: float | None = None
    unit: str | None = None

class IndicatorResponse(IndicatorBase):
    id: int
    status: IndicatorStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)