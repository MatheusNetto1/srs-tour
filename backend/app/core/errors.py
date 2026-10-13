import math
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.messages import get_message


class DomainError(Exception):
    """Base class for business errors, identified by a stable ``code``."""

    code: str = "error"


class NotFoundError(DomainError):
    code = "not_found"


class ConflictError(DomainError):
    code = "conflict"


class UnauthorizedError(DomainError):
    code = "unauthorized"


ERROR_STATUS_CODES: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
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

    # O esquema Bearer exige o cabeçalho WWW-Authenticate em toda resposta 401.
    headers = (
        {"WWW-Authenticate": "Bearer"}
        if status_code == status.HTTP_401_UNAUTHORIZED
        else None
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": get_message(error.code)},
        headers=headers,
    )


def _json_safe(value: Any) -> Any:
    """Replace NaN/Infinity, which JSON responses cannot represent, by text."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)

    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}

    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]

    return value


async def request_validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    # Mesmo formato do handler padrão do FastAPI, mas sem quebrar (500) quando o
    # valor rejeitado ecoado em `input` é NaN ou infinito.
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": jsonable_encoder(_json_safe(error.errors()))},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
