from fastapi import HTTPException, status
from indicators.models import Indicator, IndicatorStatus
from indicators.repository import IndicatorRepository
from indicators.schemas import IndicatorCreate, IndicatorUpdate


class IndicatorService:
    def __init__(self, repo: IndicatorRepository):
        self.repo = repo

    def create_indicator(self, data: IndicatorCreate) -> Indicator:
        return self.repo.create(data)

    def get_indicators(
        self, period: str | None, sector: str | None, status: IndicatorStatus | None
    ) -> list[Indicator]:
        return self.repo.get_all(period=period, sector=sector, status=status)

    def get_indicator_by_id(self, indicator_id: int) -> Indicator:
        obj = self.repo.get_by_id(indicator_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Indicador não encontrado.",
            )
        return obj

    def update_indicator(self, indicator_id: int, data: IndicatorUpdate) -> Indicator:
        obj = self.get_indicator_by_id(indicator_id)
        update_data = data.model_dump(exclude_unset=True)
        return self.repo.update(obj, update_data)

    def delete_indicator(self, indicator_id: int) -> None:
        obj = self.get_indicator_by_id(indicator_id)
        self.repo.delete(obj)

    def change_status(
        self, indicator_id: int, new_status: IndicatorStatus
    ) -> Indicator:
        obj = self.get_indicator_by_id(indicator_id)
        if obj.status == new_status:
            return obj
        return self.repo.update(obj, {"status": new_status})
