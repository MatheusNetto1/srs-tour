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
    is_active: bool | None = None,
) -> list[TourismEstablishment]:
    statement = select(TourismEstablishment)

    if category is not None:
        statement = statement.where(
            TourismEstablishment.category == category,
        )

    if is_active is not None:
        statement = statement.where(
            TourismEstablishment.is_active == is_active,
        )

    statement = statement.order_by(TourismEstablishment.id)

    return list(db.scalars(statement).all())


def get_establishment(
    db: Session,
    establishment_id: int,
    *,
    only_active: bool = False,
) -> TourismEstablishment | None:
    statement = select(TourismEstablishment).where(
        TourismEstablishment.id == establishment_id,
    )

    if only_active:
        statement = statement.where(TourismEstablishment.is_active.is_(True))

    return db.scalar(statement)


def update_establishment(
    db: Session,
    establishment: TourismEstablishment,
    data: TourismEstablishmentUpdate,
) -> TourismEstablishment:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(establishment, field, value)

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
