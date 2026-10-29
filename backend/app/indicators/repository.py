from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.indicators.models import Indicator, IndicatorStatus
from app.indicators.schemas import IndicatorCreate


class IndicatorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: IndicatorCreate, slug: str) -> Indicator:
        db_obj = Indicator(**data.model_dump(exclude={"slug"}), slug=slug)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_all(
        self,
        period: int | None = None,
        period_from: int | None = None,
        period_to: int | None = None,
        sector: str | None = None,
        slug: str | None = None,
        status: IndicatorStatus | None = None,
    ) -> list[Indicator]:
        stmt = select(Indicator)

        if period is not None:
            stmt = stmt.where(Indicator.period == period)
        if period_from is not None:
            stmt = stmt.where(Indicator.period >= period_from)
        if period_to is not None:
            stmt = stmt.where(Indicator.period <= period_to)
        if sector is not None:
            stmt = stmt.where(Indicator.sector == sector)
        if slug is not None:
            stmt = stmt.where(Indicator.slug == slug)
        if status is not None:
            stmt = stmt.where(Indicator.status == status)

        stmt = stmt.order_by(Indicator.id)

        return list(self.session.scalars(stmt).all())

    def get_latest_published(self, sector: str | None = None) -> list[Indicator]:
        """For each slug, the published row with the highest period."""
        latest = select(
            Indicator.slug,
            func.max(Indicator.period).label("period"),
        ).where(Indicator.status == IndicatorStatus.PUBLISHED)

        if sector is not None:
            latest = latest.where(Indicator.sector == sector)

        latest = latest.group_by(Indicator.slug).subquery()

        stmt = (
            select(Indicator)
            .join(
                latest,
                (Indicator.slug == latest.c.slug)
                & (Indicator.period == latest.c.period),
            )
            .where(Indicator.status == IndicatorStatus.PUBLISHED)
            .order_by(Indicator.slug)
        )

        return list(self.session.scalars(stmt).all())

    def get_by_id(self, indicator_id: int) -> Indicator | None:
        return self.session.get(Indicator, indicator_id)

    def get_by_slug_and_period(self, slug: str, period: int) -> Indicator | None:
        stmt = select(Indicator).where(
            Indicator.slug == slug,
            Indicator.period == period,
        )

        return self.session.scalar(stmt)

    def update(self, db_obj: Indicator, update_data: dict[str, Any]) -> Indicator:
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: Indicator) -> None:
        self.session.delete(db_obj)
        self.session.commit()
