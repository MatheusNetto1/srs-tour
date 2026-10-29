from app.core.errors import ConflictError, NotFoundError


class IndicatorNotFoundError(NotFoundError):
    code = "indicator.not_found"


class IndicatorAlreadyExistsError(ConflictError):
    code = "indicator.already_exists"
