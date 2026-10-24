import logging
import math
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError
from starlette.exceptions import HTTPException

from app.core.messages import get_message

logger = logging.getLogger(__name__)


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

HTTP_ERROR_CODES: dict[int, str] = {
    status.HTTP_404_NOT_FOUND: "http.not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "http.method_not_allowed",
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
        content={
            "detail": get_message(error.code),
            "code": error.code,
        },
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
    # Preserva o tratamento de NaN/Infinity antes de montar a lista C1 de `errors`.
    safe_errors = jsonable_encoder(_json_safe(error.errors()))
    errors = [
        {
            "field": ".".join(str(part) for part in item.get("loc", ())),
            "code": str(item.get("type", "")),
            "message": str(item.get("msg", "")),
        }
        for item in safe_errors
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": get_message("validation.failed"),
            "code": "validation.failed",
            "errors": errors,
        },
    )


async def http_exception_handler(
    request: Request,
    error: HTTPException,
) -> JSONResponse:
    code = HTTP_ERROR_CODES.get(error.status_code, "http.error")

    return JSONResponse(
        status_code=error.status_code,
        content={
            "detail": get_message(code),
            "code": code,
        },
        headers=error.headers,
    )


async def data_error_handler(
    request: Request,
    error: DataError,
) -> JSONResponse:
    code = "validation.invalid_value"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": get_message(code),
            "code": code,
        },
    )


async def unhandled_exception_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    logger.exception("Unhandled error while processing request", exc_info=error)
    code = "internal_error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": get_message(code),
            "code": code,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(DataError, data_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
