from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tourism.models import TourismEstablishment
from app.tourism.schemas import (
    TourismEstablishmentCreate,
    TourismEstablishmentUpdate,
)


def create_establishment(
    db: Session,
    data: TourismEstablishmentCreate,
) -> TourismEstablishment:
    establishment = TourismEstablishment(
        name=data.name,
        category=data.category,
    )

    db.add(establishment)
    db.commit()
    db.refresh(establishment)

    return establishment


def list_establishments(
    db: Session,
    category: str | None = None,
) -> list[TourismEstablishment]:
    statement = select(TourismEstablishment)

    if category is not None:
        statement = statement.where(
            TourismEstablishment.category == category,
        )

    statement = statement.order_by(TourismEstablishment.id)

    return list(db.scalars(statement).all())


def get_establishment(
    db: Session,
    establishment_id: int,
) -> TourismEstablishment | None:
    return db.get(TourismEstablishment, establishment_id)


def update_establishment(
    db: Session,
    establishment: TourismEstablishment,
    data: TourismEstablishmentUpdate,
) -> TourismEstablishment:
    establishment.name = data.name
    establishment.category = data.category
    establishment.is_active = data.is_active

    db.commit()
    db.refresh(establishment)

    return establishment


def deactivate_establishment(
    db: Session,
    establishment: TourismEstablishment,
) -> TourismEstablishment:
    establishment.is_active = False

    db.commit()
    db.refresh(establishment)

    return establishment
