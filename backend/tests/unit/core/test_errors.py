import asyncio
import json
import math

import pytest
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DataError
from starlette.exceptions import HTTPException

from app.core.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    UnauthorizedError,
    _json_safe,
    data_error_handler,
    domain_error_handler,
    http_exception_handler,
    request_validation_error_handler,
    unhandled_exception_handler,
)
from app.core.messages import get_message


def make_request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


def test_json_safe_replaces_non_finite_floats_with_text() -> None:
    errors = [
        {"loc": ["body", "value"], "input": math.nan},
        {"loc": ["body", "other"], "input": [math.inf, -math.inf, 1.5]},
    ]

    assert _json_safe(errors) == [
        {"loc": ["body", "value"], "input": "nan"},
        {"loc": ["body", "other"], "input": ["inf", "-inf", 1.5]},
    ]


def test_json_safe_keeps_regular_values_untouched() -> None:
    errors = [{"loc": ["body", "name"], "input": "x", "ctx": {"min_length": 1}}]

    assert _json_safe(errors) == errors


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_code"),
    [
        (NotFoundError(), status.HTTP_404_NOT_FOUND, "not_found"),
        (ConflictError(), status.HTTP_409_CONFLICT, "conflict"),
        (UnauthorizedError(), status.HTTP_401_UNAUTHORIZED, "unauthorized"),
        (DomainError(), status.HTTP_400_BAD_REQUEST, "error"),
    ],
)
def test_domain_error_handler_returns_detail_and_code(
    error: DomainError,
    expected_status: int,
    expected_code: str,
) -> None:
    response = asyncio.run(domain_error_handler(make_request(), error))
    body = json.loads(response.body)

    assert response.status_code == expected_status
    assert body == {
        "detail": get_message(expected_code),
        "code": expected_code,
    }
    assert body["detail"] != expected_code


def test_domain_error_handler_sets_www_authenticate_on_401() -> None:
    response = asyncio.run(domain_error_handler(make_request(), UnauthorizedError()))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["www-authenticate"] == "Bearer"


def test_request_validation_error_handler_formats_errors_and_handles_nan() -> None:
    validation_error = RequestValidationError(
        errors=[
            {
                "loc": ("body", "name"),
                "msg": "String should have at least 3 characters",
                "type": "string_too_short",
                "input": "ab",
            },
            {
                "loc": ("body", "value"),
                "msg": "Input should be a finite number",
                "type": "finite_number",
                "input": math.nan,
            },
        ]
    )

    response = asyncio.run(
        request_validation_error_handler(make_request(), validation_error)
    )
    body = json.loads(response.body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert body == {
        "detail": "Dados inválidos.",
        "code": "validation.failed",
        "errors": [
            {
                "field": "body.name",
                "code": "string_too_short",
                "message": "String should have at least 3 characters",
            },
            {
                "field": "body.value",
                "code": "finite_number",
                "message": "Input should be a finite number",
            },
        ],
    }


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (status.HTTP_404_NOT_FOUND, "http.not_found"),
        (status.HTTP_405_METHOD_NOT_ALLOWED, "http.method_not_allowed"),
        (status.HTTP_400_BAD_REQUEST, "http.error"),
        (status.HTTP_418_IM_A_TEAPOT, "http.error"),
    ],
)
def test_http_exception_handler_maps_status_to_error_envelope(
    status_code: int,
    expected_code: str,
) -> None:
    exc = HTTPException(status_code=status_code, detail="Raw detail")

    response = asyncio.run(http_exception_handler(make_request(), exc))
    body = json.loads(response.body)

    assert response.status_code == status_code
    assert body == {
        "detail": get_message(expected_code),
        "code": expected_code,
    }


def test_http_exception_handler_forwards_headers() -> None:
    exc = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Method Not Allowed",
        headers={"Allow": "GET, HEAD"},
    )

    response = asyncio.run(http_exception_handler(make_request(), exc))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.headers["allow"] == "GET, HEAD"


def test_data_error_handler_returns_422_invalid_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    exc = DataError("SELECT 1", {}, Exception("integer out of range"))

    with caplog.at_level("WARNING"):
        response = asyncio.run(data_error_handler(make_request(), exc))
    body = json.loads(response.body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert body == {
        "detail": get_message("validation.invalid_value"),
        "code": "validation.invalid_value",
    }
    assert "integer out of range" in caplog.text


def test_unhandled_exception_handler_returns_500_without_leaking_details() -> None:
    exc = RuntimeError("detalhe interno sensivel do banco")

    response = asyncio.run(unhandled_exception_handler(make_request(), exc))
    body = json.loads(response.body)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert body == {
        "detail": get_message("internal_error"),
        "code": "internal_error",
    }
    assert "sensivel" not in response.body.decode()
