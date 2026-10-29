from sqlalchemy.exc import IntegrityError

from app.indicators.exceptions import (
    IndicatorAlreadyExistsError,
    IndicatorNotFoundError,
)
from app.indicators.models import Indicator, IndicatorStatus
from app.indicators.repository import IndicatorRepository
from app.indicators.schemas import IndicatorCreate, IndicatorUpdate
from app.indicators.slug import slugify


class IndicatorService:
    def __init__(self, repo: IndicatorRepository) -> None:
        self.repo = repo

    # Leitura pública: expõe somente indicadores PUBLISHED.

    def list_published(
        self,
        period: int | None = None,
        period_from: int | None = None,
        period_to: int | None = None,
        sector: str | None = None,
        slug: str | None = None,
    ) -> list[Indicator]:
        return self.repo.get_all(
            period=period,
            period_from=period_from,
            period_to=period_to,
            sector=sector,
            slug=slug,
            status=IndicatorStatus.PUBLISHED,
        )

    def list_latest_published(self, sector: str | None = None) -> list[Indicator]:
        return self.repo.get_latest_published(sector)

    def get_published(self, indicator_id: int) -> Indicator:
        indicator = self.repo.get_by_id(indicator_id)

        if indicator is None or indicator.status != IndicatorStatus.PUBLISHED:
            raise IndicatorNotFoundError

        return indicator

    # Operações administrativas: enxergam indicadores em qualquer status.

    def list_indicators(
        self,
        period: int | None = None,
        period_from: int | None = None,
        period_to: int | None = None,
        sector: str | None = None,
        slug: str | None = None,
        status: IndicatorStatus | None = None,
    ) -> list[Indicator]:
        return self.repo.get_all(
            period=period,
            period_from=period_from,
            period_to=period_to,
            sector=sector,
            slug=slug,
            status=status,
        )

    def get_indicator(self, indicator_id: int) -> Indicator:
        indicator = self.repo.get_by_id(indicator_id)

        if indicator is None:
            raise IndicatorNotFoundError

        return indicator

    def create_indicator(self, data: IndicatorCreate) -> Indicator:
        slug = data.slug or slugify(data.name)

        if self.repo.get_by_slug_and_period(slug, data.period) is not None:
            raise IndicatorAlreadyExistsError

        try:
            return self.repo.create(data, slug)
        except IntegrityError as error:
            self.repo.session.rollback()
            raise IndicatorAlreadyExistsError from error

    def update_indicator(
        self,
        indicator_id: int,
        data: IndicatorUpdate,
    ) -> Indicator:
        indicator = self.get_indicator(indicator_id)
        existing = self.repo.get_by_slug_and_period(indicator.slug, data.period)

        if existing is not None and existing.id != indicator.id:
            raise IndicatorAlreadyExistsError

        try:
            return self.repo.update(indicator, data.model_dump())
        except IntegrityError as error:
            self.repo.session.rollback()
            raise IndicatorAlreadyExistsError from error

    def delete_indicator(self, indicator_id: int) -> None:
        indicator = self.get_indicator(indicator_id)

        self.repo.delete(indicator)

    def change_status(
        self,
        indicator_id: int,
        new_status: IndicatorStatus,
    ) -> Indicator:
        indicator = self.get_indicator(indicator_id)

        if indicator.status == new_status:
            return indicator

        return self.repo.update(indicator, {"status": new_status})
