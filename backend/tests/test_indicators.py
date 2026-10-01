import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def base_indicator():
    return {
        "name": "Ocupação Hoteleira",
        "sector": "Hospedagem",
        "period": "2026",
        "value": 75.5,
        "unit": "%",
    }


def test_create_indicator(base_indicator):
    response = client.post("/api/v1/indicators", json=base_indicator)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == base_indicator["name"]
    assert data["status"] == "DRAFT"
    assert "id" in data


def test_validate_mandatory_fields():
    response = client.post("/api/v1/indicators", json={"name": "Incompleto"})
    assert response.status_code == 422


def test_list_and_filters(base_indicator):
    client.post("/api/v1/indicators", json=base_indicator)
    client.post(
        "/api/v1/indicators",
        json={
            "name": "Chegadas",
            "sector": "Transporte",
            "period": "2025",
            "value": 100,
            "unit": "mil",
        },
    )

    resp_all = client.get("/api/v1/indicators")
    assert len(resp_all.json()) >= 2

    resp_period = client.get("/api/v1/indicators?period=2026")
    assert all(ind["period"] == "2026" for ind in resp_period.json())

    resp_sector = client.get("/api/v1/indicators?sector=Hospedagem")
    assert all(ind["sector"] == "Hospedagem" for ind in resp_sector.json())

    resp_combined = client.get("/api/v1/indicators?period=2025&sector=Transporte")
    assert len(resp_combined.json()) > 0
    assert resp_combined.json()[0]["name"] == "Chegadas"


def test_get_by_id(base_indicator):
    create_resp = client.post("/api/v1/indicators", json=base_indicator)
    ind_id = create_resp.json()["id"]

    resp = client.get(f"/api/v1/indicators/{ind_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == ind_id


def test_update_indicator(base_indicator):
    create_resp = client.post("/api/v1/indicators", json=base_indicator)
    ind_id = create_resp.json()["id"]

    update_resp = client.put(f"/api/v1/indicators/{ind_id}", json={"value": 80.0})
    assert update_resp.status_code == 200
    assert update_resp.json()["value"] == 80.0
    assert update_resp.json()["sector"] == "Hospedagem"


def test_publish_and_unpublish(base_indicator):
    create_resp = client.post("/api/v1/indicators", json=base_indicator)
    ind_id = create_resp.json()["id"]

    pub_resp = client.patch(f"/api/v1/indicators/{ind_id}/publish")
    assert pub_resp.status_code == 200
    assert pub_resp.json()["status"] == "PUBLISHED"

    pub_list = client.get("/api/v1/indicators?status=PUBLISHED")
    assert any(ind["id"] == ind_id for ind in pub_list.json())

    unpub_resp = client.patch(f"/api/v1/indicators/{ind_id}/unpublish")
    assert unpub_resp.status_code == 200
    assert unpub_resp.json()["status"] == "DRAFT"


def test_delete_indicator(base_indicator):
    create_resp = client.post("/api/v1/indicators", json=base_indicator)
    ind_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/indicators/{ind_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/indicators/{ind_id}")
    assert get_resp.status_code == 404
