from fastapi import APIRouter, Query, Response, status

from app.core.dependencies import DbSession
from app.tourism import service
from app.tourism.schemas import (
    TourismEstablishmentCreate,
    TourismEstablishmentResponse,
    TourismEstablishmentUpdate,
)

router = APIRouter()
admin_router = APIRouter()


@admin_router.post(
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
    return service.list_establishments(db, category, is_active=True)


@router.get(
    "/establishments/{establishment_id}",
    response_model=TourismEstablishmentResponse,
)
def get_establishment(
    establishment_id: int,
    db: DbSession,
) -> TourismEstablishmentResponse:
    return service.get_establishment(db, establishment_id, only_active=True)


@admin_router.get(
    "/establishments",
    response_model=list[TourismEstablishmentResponse],
)
def list_admin_establishments(
    db: DbSession,
    category: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> list[TourismEstablishmentResponse]:
    return service.list_establishments(db, category, is_active)


@admin_router.get(
    "/establishments/{establishment_id}",
    response_model=TourismEstablishmentResponse,
)
def get_admin_establishment(
    establishment_id: int,
    db: DbSession,
) -> TourismEstablishmentResponse:
    return service.get_establishment(db, establishment_id)


@admin_router.put(
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


@admin_router.delete(
    "/establishments/{establishment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_establishment(
    establishment_id: int,
    db: DbSession,
) -> Response:
    service.deactivate_establishment(db, establishment_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
