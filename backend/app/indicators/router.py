from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from indicators import schemas, models
from indicators.repository import IndicatorRepository
from indicators.service import IndicatorService

router = APIRouter(prefix="/api/v1/indicators", tags=["Indicators"])

def get_indicator_service(db: Session = Depends(get_db)) -> IndicatorService:
    repo = IndicatorRepository(db)
    return IndicatorService(repo)

@router.get("", response_model=list[schemas.IndicatorResponse])
def list_indicators(
    period: str | None = Query(None, description="Filtrar por período (ex: 2026)"),
    sector: str | None = Query(None, description="Filtrar por setor (ex: Hospedagem)"),
    status: models.IndicatorStatus | None = Query(
        None, description="O dashboard público deve passar ?status=PUBLISHED"
    ),
    service: IndicatorService = Depends(get_indicator_service)
):
    return service.get_indicators(period, sector, status)

@router.get("/{id}", response_model=schemas.IndicatorResponse)
def get_indicator(id: int, service: IndicatorService = Depends(get_indicator_service)):
    return service.get_indicator_by_id(id)

@router.post("", response_model=schemas.IndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_indicator(data: schemas.IndicatorCreate, service: IndicatorService = Depends(get_indicator_service)):
    return service.create_indicator(data)

@router.put("/{id}", response_model=schemas.IndicatorResponse)
def update_indicator(
    id: int, data: schemas.IndicatorUpdate, service: IndicatorService = Depends(get_indicator_service)
):
    return service.update_indicator(id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(id: int, service: IndicatorService = Depends(get_indicator_service)):
    service.delete_indicator(id)

@router.patch("/{id}/publish", response_model=schemas.IndicatorResponse)
def publish_indicator(id: int, service: IndicatorService = Depends(get_indicator_service)):
    return service.change_status(id, models.IndicatorStatus.PUBLISHED)

@router.patch("/{id}/unpublish", response_model=schemas.IndicatorResponse)
def unpublish_indicator(id: int, service: IndicatorService = Depends(get_indicator_service)):
    return service.change_status(id, models.IndicatorStatus.DRAFT)