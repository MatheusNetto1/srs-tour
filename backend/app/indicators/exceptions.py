from app.core.errors import NotFoundError


class IndicatorNotFoundError(NotFoundError):
    code = "indicator.not_found"
