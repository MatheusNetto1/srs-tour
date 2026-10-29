from sqlalchemy.orm import Session

from app.tourism import repository
from app.tourism.exceptions import TourismEstablishmentNotFoundError
from app.tourism.models import TourismEstablishment
from app.tourism.schemas import (
    TourismEstablishmentCreate,
    TourismEstablishmentUpdate,
)


def create_establishment(
    db: Session,
    data: TourismEstablishmentCreate,
) -> TourismEstablishment:
    return repository.create_establishment(db, data)


def list_establishments(
    db: Session,
    category: str | None = None,
    is_active: bool | None = None,
) -> list[TourismEstablishment]:
    return repository.list_establishments(db, category, is_active)


def get_establishment(
    db: Session,
    establishment_id: int,
    *,
    only_active: bool = False,
) -> TourismEstablishment:
    establishment = repository.get_establishment(
        db,
        establishment_id,
        only_active=only_active,
    )

    if establishment is None:
        raise TourismEstablishmentNotFoundError

    return establishment


def update_establishment(
    db: Session,
    establishment_id: int,
    data: TourismEstablishmentUpdate,
) -> TourismEstablishment:
    establishment = get_establishment(db, establishment_id)

    return repository.update_establishment(
        db,
        establishment,
        data,
    )


def deactivate_establishment(
    db: Session,
    establishment_id: int,
) -> TourismEstablishment:
    establishment = get_establishment(db, establishment_id)

    return repository.deactivate_establishment(
        db,
        establishment,
    )
