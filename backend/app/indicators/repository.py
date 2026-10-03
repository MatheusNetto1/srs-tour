from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.indicators.models import Indicator, IndicatorStatus
from app.indicators.schemas import IndicatorCreate


class IndicatorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: IndicatorCreate) -> Indicator:
        db_obj = Indicator(**data.model_dump())
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_all(
        self,
        period: str | None = None,
        sector: str | None = None,
        status: IndicatorStatus | None = None,
    ) -> list[Indicator]:
        stmt = select(Indicator)

        if period is not None:
            stmt = stmt.where(Indicator.period == period)
        if sector is not None:
            stmt = stmt.where(Indicator.sector == sector)
        if status is not None:
            stmt = stmt.where(Indicator.status == status)

        stmt = stmt.order_by(Indicator.id)

        return list(self.session.scalars(stmt).all())

    def get_by_id(self, indicator_id: int) -> Indicator | None:
        return self.session.get(Indicator, indicator_id)

    def update(self, db_obj: Indicator, update_data: dict[str, Any]) -> Indicator:
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: Indicator) -> None:
        self.session.delete(db_obj)
        self.session.commit()
