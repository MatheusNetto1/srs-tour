from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.messages import get_message


class DomainError(Exception):
    """Base class for business errors, identified by a stable ``code``."""

    code: str = "error"


class NotFoundError(DomainError):
    code = "not_found"


class ConflictError(DomainError):
    code = "conflict"


ERROR_STATUS_CODES: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
}


async def domain_error_handler(
    request: Request,
    error: DomainError,
) -> JSONResponse:
    status_code = next(
        (
            code
            for error_type, code in ERROR_STATUS_CODES.items()
            if isinstance(error, error_type)
        ),
        status.HTTP_400_BAD_REQUEST,
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": get_message(error.code)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
