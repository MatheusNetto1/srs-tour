from app.core.errors import NotFoundError


class TourismEstablishmentNotFoundError(NotFoundError):
    code = "tourism_establishment.not_found"
