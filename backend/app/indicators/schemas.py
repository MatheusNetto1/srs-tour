from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.indicators.models import IndicatorStatus

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


def _text(max_length: int) -> StringConstraints:
    return StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=max_length,
    )


# Os limites acompanham exatamente o tamanho das colunas em `indicators`.
IndicatorName = Annotated[str, _text(255)]
IndicatorSector = Annotated[str, _text(100)]
IndicatorUnit = Annotated[str, _text(50)]
IndicatorValue = Annotated[float, Field(allow_inf_nan=False)]
IndicatorPeriod = Annotated[int, Field(ge=1900, le=2100)]
IndicatorSlug = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
        pattern=SLUG_PATTERN,
    ),
]


class IndicatorBase(BaseModel):
    name: IndicatorName = Field(description="Nome do indicador")
    sector: IndicatorSector = Field(description="Setor relacionado, ex: Hospedagem")
    period: IndicatorPeriod = Field(description="Ano de referência, ex: 2026")
    value: IndicatorValue = Field(description="Valor numérico do indicador")
    unit: IndicatorUnit = Field(description="Unidade de medida, ex: % ou R$")


class IndicatorCreate(IndicatorBase):
    # `status`, `id` e timestamps são controlados pelo servidor.
    model_config = ConfigDict(extra="forbid")

    slug: IndicatorSlug | None = Field(
        default=None,
        description=(
            "Identificador estável da série (ex: meios-de-hospedagem); "
            "se omitido, é derivado do nome"
        ),
    )


class IndicatorUpdate(IndicatorBase):
    # PUT substitui todos os campos editáveis; `slug` é imutável e fica de fora.
    model_config = ConfigDict(extra="forbid")


class IndicatorResponse(BaseModel):
    """Dado persistido, serializado como está.

    Não reaplica as regras de entrada (strip, tamanho, não vazio): um registro
    legado ou gravado fora da API não deve causar erro de validação na saída.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(description="Nome do indicador")
    slug: str = Field(description="Identificador estável da série")
    sector: str = Field(description="Setor relacionado, ex: Hospedagem")
    period: int = Field(description="Ano de referência, ex: 2026")
    value: float = Field(description="Valor numérico do indicador")
    unit: str = Field(description="Unidade de medida, ex: % ou R$")
    status: IndicatorStatus
    created_at: datetime
    updated_at: datetime
