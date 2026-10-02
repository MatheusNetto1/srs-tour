from fastapi import APIRouter, Query, Response, status

from app.core.dependencies import DbSession
from app.tourism import service
from app.tourism.schemas import (
    TourismEstablishmentCreate,
    TourismEstablishmentResponse,
    TourismEstablishmentUpdate,
)

router = APIRouter()


@router.post(
    "/establishments",
    response_model=TourismEstablishmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_establishment(
    data: TourismEstablishmentCreate,
    db: DbSession,
) -> TourismEstablishmentResponse:
    return service.create_establishment(db, data)


@router.get(
    "/establishments",
    response_model=list[TourismEstablishmentResponse],
)
def list_establishments(
    db: DbSession,
    category: str | None = Query(default=None),
) -> list[TourismEstablishmentResponse]:
    return service.list_establishments(db, category)


@router.get(
    "/establishments/{establishment_id}",
    response_model=TourismEstablishmentResponse,
)
def get_establishment(
    establishment_id: int,
    db: DbSession,
) -> TourismEstablishmentResponse:
    return service.get_establishment(db, establishment_id)


@router.put(
    "/establishments/{establishment_id}",
    response_model=TourismEstablishmentResponse,
)
def update_establishment(
    establishment_id: int,
    data: TourismEstablishmentUpdate,
    db: DbSession,
) -> TourismEstablishmentResponse:
    return service.update_establishment(
        db,
        establishment_id,
        data,
    )


@router.delete(
    "/establishments/{establishment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_establishment(
    establishment_id: int,
    db: DbSession,
) -> Response:
    service.deactivate_establishment(db, establishment_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
