from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.indicators.models import IndicatorStatus


def _text(max_length: int) -> StringConstraints:
    return StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=max_length,
    )


# Os limites acompanham exatamente o tamanho das colunas em `indicators`.
IndicatorName = Annotated[str, _text(255)]
IndicatorSector = Annotated[str, _text(100)]
IndicatorPeriod = Annotated[str, _text(50)]
IndicatorUnit = Annotated[str, _text(50)]
IndicatorValue = Annotated[float, Field(allow_inf_nan=False)]


class IndicatorBase(BaseModel):
    name: IndicatorName = Field(description="Nome do indicador")
    sector: IndicatorSector = Field(description="Setor relacionado, ex: Hospedagem")
    period: IndicatorPeriod = Field(description="Período de referência, ex: 2026")
    value: IndicatorValue = Field(description="Valor numérico do indicador")
    unit: IndicatorUnit = Field(description="Unidade de medida, ex: % ou R$")


class IndicatorCreate(IndicatorBase):
    # `status`, `id` e timestamps são controlados pelo servidor.
    model_config = ConfigDict(extra="forbid")


class IndicatorUpdate(IndicatorBase):
    # PUT substitui todos os campos editáveis.
    model_config = ConfigDict(extra="forbid")


class IndicatorResponse(BaseModel):
    """Dado persistido, serializado como está.

    Não reaplica as regras de entrada (strip, tamanho, não vazio): um registro
    legado ou gravado fora da API não deve causar erro de validação na saída.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(description="Nome do indicador")
    sector: str = Field(description="Setor relacionado, ex: Hospedagem")
    period: str = Field(description="Período de referência, ex: 2026")
    value: float = Field(description="Valor numérico do indicador")
    unit: str = Field(description="Unidade de medida, ex: % ou R$")
    status: IndicatorStatus
    created_at: datetime
    updated_at: datetime
