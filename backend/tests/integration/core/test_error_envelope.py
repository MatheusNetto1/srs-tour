from fastapi import status
from fastapi.testclient import TestClient

from app.core.messages import get_message


def test_unknown_route_returns_404_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/rota-inexistente")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": get_message("http.not_found"),
        "code": "http.not_found",
    }


def test_method_not_allowed_returns_405_envelope(client: TestClient) -> None:
    response = client.post("/api/v1/indicators")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {
        "detail": get_message("http.method_not_allowed"),
        "code": "http.method_not_allowed",
    }


def test_validation_error_returns_422_envelope_with_field_errors(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/admin/indicators",
        json={
            "name": "",
            "sector": "Hospedagem",
            "period": "2026",
            "value": 75.5,
            "unit": "%",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    body = response.json()

    assert body["detail"] == "Dados inválidos."
    assert body["code"] == "validation.failed"
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) >= 1
    assert body["errors"][0]["field"] == "body.name"
    assert isinstance(body["errors"][0]["code"], str)
    assert isinstance(body["errors"][0]["message"], str)


def test_id_out_of_int4_range_returns_422_invalid_value(client: TestClient) -> None:
    response = client.get("/api/v1/indicators/99999999999999")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {
        "detail": get_message("validation.invalid_value"),
        "code": "validation.invalid_value",
    }


def test_nul_byte_in_text_field_returns_422_invalid_value(client: TestClient) -> None:
    response = client.post(
        "/api/v1/admin/indicators",
        json={
            "name": "a\u0000bc",
            "sector": "Hospedagem",
            "period": "2026",
            "value": 75.5,
            "unit": "%",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {
        "detail": get_message("validation.invalid_value"),
        "code": "validation.invalid_value",
    }


def test_existing_domain_error_details_remain_unchanged(client: TestClient) -> None:
    indicator_res = client.get("/api/v1/indicators/999999")
    assert indicator_res.status_code == status.HTTP_404_NOT_FOUND
    assert indicator_res.json() == {
        "detail": "Indicador não encontrado.",
        "code": "indicator.not_found",
    }
