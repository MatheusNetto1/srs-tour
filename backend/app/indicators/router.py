from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
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
    str | None,
    Query(description="Filtrar por período (ex: 2026)"),
]
SectorQuery = Annotated[
    str | None,
    Query(description="Filtrar por setor (ex: Hospedagem)"),
]

# Leitura pública (/api/v1/indicators): retorna SOMENTE indicadores PUBLISHED.
# Rascunhos nunca são expostos por estas rotas, independentemente dos parâmetros.
router = APIRouter(tags=["Indicators"])

# Rotas administrativas (/api/v1/admin/indicators): leitura de qualquer status e
# toda alteração. O prefixo é aplicado pelo agregador em app/api/v1/router.py.
admin_router = APIRouter(tags=["Indicators (admin)"])


@router.get("", response_model=list[IndicatorResponse])
def list_indicators(
    service: ServiceDep,
    period: PeriodQuery = None,
    sector: SectorQuery = None,
) -> list[Indicator]:
    return service.list_published(period, sector)


@router.get("/{indicator_id}", response_model=IndicatorResponse)
def get_indicator(indicator_id: int, service: ServiceDep) -> Indicator:
    return service.get_published(indicator_id)


@admin_router.get("", response_model=list[IndicatorResponse])
def admin_list_indicators(
    service: ServiceDep,
    period: PeriodQuery = None,
    sector: SectorQuery = None,
    status: Annotated[
        IndicatorStatus | None,
        Query(description="Filtrar por status (DRAFT ou PUBLISHED)"),
    ] = None,
) -> list[Indicator]:
    return service.list_indicators(period, sector, status)


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
