from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from indicators import models, schemas
from indicators.repository import IndicatorRepository
from indicators.service import IndicatorService
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

router = APIRouter(prefix="/api/v1/indicators", tags=["Indicators"])

DbDep = Annotated[Session, Depends(get_db)]


def get_indicator_service(db: DbDep) -> IndicatorService:
    repo = IndicatorRepository(db)
    return IndicatorService(repo)


ServiceDep = Annotated[IndicatorService, Depends(get_indicator_service)]


@router.get("", response_model=list[schemas.IndicatorResponse])
def list_indicators(
    service: ServiceDep,
    period: Annotated[
        str | None, Query(description="Filtrar por período (ex: 2026)")
    ] = None,
    sector: Annotated[
        str | None, Query(description="Filtrar por setor (ex: Hospedagem)")
    ] = None,
    status: Annotated[
        models.IndicatorStatus | None,
        Query(description="O dashboard público deve passar ?status=PUBLISHED"),
    ] = None,
):
    return service.get_indicators(period, sector, status)


@router.get("/{id}", response_model=schemas.IndicatorResponse)
def get_indicator(id: int, service: ServiceDep):
    return service.get_indicator_by_id(id)


@router.post(
    "", response_model=schemas.IndicatorResponse, status_code=status.HTTP_201_CREATED
)
def create_indicator(data: schemas.IndicatorCreate, service: ServiceDep):
    return service.create_indicator(data)


@router.put("/{id}", response_model=schemas.IndicatorResponse)
def update_indicator(id: int, data: schemas.IndicatorUpdate, service: ServiceDep):
    return service.update_indicator(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(id: int, service: ServiceDep):
    service.delete_indicator(id)


@router.patch("/{id}/publish", response_model=schemas.IndicatorResponse)
def publish_indicator(id: int, service: ServiceDep):
    return service.change_status(id, models.IndicatorStatus.PUBLISHED)


@router.patch("/{id}/unpublish", response_model=schemas.IndicatorResponse)
def unpublish_indicator(id: int, service: ServiceDep):
    return service.change_status(id, models.IndicatorStatus.DRAFT)
