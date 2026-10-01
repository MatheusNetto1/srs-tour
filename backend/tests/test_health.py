from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_v1_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
    }