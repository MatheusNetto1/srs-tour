from app.core.errors import NotFoundError


class ReportNotFoundError(NotFoundError):
    code = "report.not_found"
