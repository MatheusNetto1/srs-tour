from app.indicators.exceptions import IndicatorNotFoundError
from app.indicators.models import Indicator, IndicatorStatus
from app.indicators.repository import IndicatorRepository
from app.indicators.schemas import IndicatorCreate, IndicatorUpdate


class IndicatorService:
    def __init__(self, repo: IndicatorRepository) -> None:
        self.repo = repo

    # Leitura pública: expõe somente indicadores PUBLISHED.

    def list_published(
        self,
        period: str | None = None,
        sector: str | None = None,
    ) -> list[Indicator]:
        return self.repo.get_all(
            period=period,
            sector=sector,
            status=IndicatorStatus.PUBLISHED,
        )

    def get_published(self, indicator_id: int) -> Indicator:
        indicator = self.repo.get_by_id(indicator_id)

        if indicator is None or indicator.status != IndicatorStatus.PUBLISHED:
            raise IndicatorNotFoundError

        return indicator

    # Operações administrativas: enxergam indicadores em qualquer status.

    def list_indicators(
        self,
        period: str | None = None,
        sector: str | None = None,
        status: IndicatorStatus | None = None,
    ) -> list[Indicator]:
        return self.repo.get_all(period=period, sector=sector, status=status)

    def get_indicator(self, indicator_id: int) -> Indicator:
        indicator = self.repo.get_by_id(indicator_id)

        if indicator is None:
            raise IndicatorNotFoundError

        return indicator

    def create_indicator(self, data: IndicatorCreate) -> Indicator:
        return self.repo.create(data)

    def update_indicator(
        self,
        indicator_id: int,
        data: IndicatorUpdate,
    ) -> Indicator:
        indicator = self.get_indicator(indicator_id)

        return self.repo.update(indicator, data.model_dump())

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
