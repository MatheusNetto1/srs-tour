from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi import status as http_status

from app.core.dependencies import DbSession
from app.indicators.models import Indicator, IndicatorStatus
from app.indicators.repository import IndicatorRepository
from app.indicators.schemas import (
    IndicatorCreate,
    IndicatorResponse,
    IndicatorUpdate,
)
from app.indicators.service import IndicatorService


def get_indicator_service(db: DbSession) -> IndicatorService:
    return IndicatorService(IndicatorRepository(db))


ServiceDep = Annotated[IndicatorService, Depends(get_indicator_service)]

PeriodQuery = Annotated[
    int | None,
    Query(description="Filtrar por período exato (ano, ex: 2026)"),
]
PeriodFromQuery = Annotated[
    int | None,
    Query(description="Filtrar pelo período inicial, inclusive (ano)"),
]
PeriodToQuery = Annotated[
    int | None,
    Query(description="Filtrar pelo período final, inclusive (ano)"),
]
SectorQuery = Annotated[
    str | None,
    Query(description="Filtrar por setor (ex: Hospedagem)"),
]
SlugQuery = Annotated[
    str | None,
    Query(description="Filtrar pelo slug da série (ex: meios-de-hospedagem)"),
]


def _validate_period_range(period_from: int | None, period_to: int | None) -> None:
    if period_from is not None and period_to is not None and period_from > period_to:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="period_from não pode ser maior que period_to.",
        )


# Leitura pública (/api/v1/indicators): retorna SOMENTE indicadores PUBLISHED.
# Rascunhos nunca são expostos por estas rotas, independentemente dos parâmetros.
router = APIRouter(tags=["Indicators"])

# Rotas administrativas (/api/v1/admin/indicators): leitura de qualquer status e
# toda alteração. O prefixo é aplicado pelo agregador em app/api/v1/router.py.
admin_router = APIRouter(tags=["Indicators (admin)"])


# "/latest" precisa ser declarada antes de "/{indicator_id}": caso contrário o
# FastAPI tenta converter "latest" para int e responde 422 em vez de 200.
@router.get("/latest", response_model=list[IndicatorResponse])
def list_latest_indicators(
    service: ServiceDep,
    sector: SectorQuery = None,
) -> list[Indicator]:
    return service.list_latest_published(sector)


@router.get("", response_model=list[IndicatorResponse])
def list_indicators(
    service: ServiceDep,
    period: PeriodQuery = None,
    period_from: PeriodFromQuery = None,
    period_to: PeriodToQuery = None,
    sector: SectorQuery = None,
    slug: SlugQuery = None,
) -> list[Indicator]:
    _validate_period_range(period_from, period_to)

    return service.list_published(period, period_from, period_to, sector, slug)


@router.get("/{indicator_id}", response_model=IndicatorResponse)
def get_indicator(indicator_id: int, service: ServiceDep) -> Indicator:
    return service.get_published(indicator_id)


@admin_router.get("", response_model=list[IndicatorResponse])
def admin_list_indicators(
    service: ServiceDep,
    period: PeriodQuery = None,
    period_from: PeriodFromQuery = None,
    period_to: PeriodToQuery = None,
    sector: SectorQuery = None,
    slug: SlugQuery = None,
    status: Annotated[
        IndicatorStatus | None,
        Query(description="Filtrar por status (draft ou published)"),
    ] = None,
) -> list[Indicator]:
    _validate_period_range(period_from, period_to)

    return service.list_indicators(
        period,
        period_from,
        period_to,
        sector,
        slug,
        status,
    )


@admin_router.get("/{indicator_id}", response_model=IndicatorResponse)
def admin_get_indicator(indicator_id: int, service: ServiceDep) -> Indicator:
    return service.get_indicator(indicator_id)


@admin_router.post(
    "",
    response_model=IndicatorResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_indicator(data: IndicatorCreate, service: ServiceDep) -> Indicator:
    return service.create_indicator(data)


@admin_router.put("/{indicator_id}", response_model=IndicatorResponse)
def update_indicator(
    indicator_id: int,
    data: IndicatorUpdate,
    service: ServiceDep,
) -> Indicator:
    return service.update_indicator(indicator_id, data)


@admin_router.delete(
    "/{indicator_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_indicator(indicator_id: int, service: ServiceDep) -> Response:
    service.delete_indicator(indicator_id)

    return Response(status_code=http_status.HTTP_204_NO_CONTENT)


@admin_router.patch("/{indicator_id}/publish", response_model=IndicatorResponse)
def publish_indicator(indicator_id: int, service: ServiceDep) -> Indicator:
    return service.change_status(indicator_id, IndicatorStatus.PUBLISHED)


@admin_router.patch("/{indicator_id}/unpublish", response_model=IndicatorResponse)
def unpublish_indicator(indicator_id: int, service: ServiceDep) -> Indicator:
    return service.change_status(indicator_id, IndicatorStatus.DRAFT)
