import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.dependencies import get_db
from app.main import app
from app.reports.models import Report  # noqa: F401

test_engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)

REPORTS_URL = "/api/v1/reports"

VALID_PAYLOAD = {
    "title": "Boletim 2026",
    "description": "Boletim trimestral do Observatório",
    "category": "Pesquisa",
    "year": 2026,
}


@pytest.fixture(autouse=True)
def database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.pop(get_db, None)


def create_report(client: TestClient, **overrides) -> dict:
    response = client.post(REPORTS_URL, json={**VALID_PAYLOAD, **overrides})

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def create_published_report(client: TestClient, **overrides) -> dict:
    report = create_report(client, **overrides)
    response = client.patch(f"{REPORTS_URL}/{report['id']}/publish")

    assert response.status_code == status.HTTP_200_OK

    return response.json()


def test_create_report_starts_as_draft(client: TestClient):
    response = client.post(REPORTS_URL, json=VALID_PAYLOAD)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["id"] > 0
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["description"] == VALID_PAYLOAD["description"]
    assert data["category"] == VALID_PAYLOAD["category"]
    assert data["year"] == VALID_PAYLOAD["year"]
    assert data["status"] == "draft"
    assert data["published_at"] is None
    assert data["file_path"] is None
    assert data["created_at"]
    assert data["updated_at"]


def test_create_report_without_description(client: TestClient):
    payload = {
        key: value for key, value in VALID_PAYLOAD.items() if key != "description"
    }

    response = client.post(REPORTS_URL, json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["description"] is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": "ab"},
        {"title": ""},
        {"category": "x"},
        {"year": 1800},
        {"year": 2200},
        {"year": "abc"},
    ],
)
def test_create_report_rejects_invalid_metadata(client: TestClient, overrides: dict):
    response = client.post(REPORTS_URL, json={**VALID_PAYLOAD, **overrides})

    assert response.status_code == 422


@pytest.mark.parametrize("missing_field", ["title", "category", "year"])
def test_create_report_requires_mandatory_fields(
    client: TestClient,
    missing_field: str,
):
    payload = {
        key: value for key, value in VALID_PAYLOAD.items() if key != missing_field
    }

    response = client.post(REPORTS_URL, json=payload)

    assert response.status_code == 422


def test_list_reports_hides_drafts(client: TestClient):
    create_report(client)

    response = client.get(REPORTS_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_reports_returns_only_published(client: TestClient):
    create_report(client, title="Rascunho interno")
    published = create_published_report(client, title="Boletim publicado")

    response = client.get(REPORTS_URL)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == published["id"]
    assert data[0]["status"] == "published"


def test_list_reports_filters_by_year(client: TestClient):
    create_published_report(client, title="Boletim 2026", year=2026)
    create_published_report(client, title="Boletim 2025", year=2025)

    response = client.get(REPORTS_URL, params={"year": 2026})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["year"] == 2026


def test_list_reports_filters_by_category_ignoring_case(client: TestClient):
    create_published_report(client, title="Pesquisa anual", category="Pesquisa")
    create_published_report(client, title="Estudo setorial", category="Estudo")

    response = client.get(REPORTS_URL, params={"category": "pesquisa"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Pesquisa"


def test_list_reports_combines_filters(client: TestClient):
    create_published_report(
        client, title="Pesquisa 2026", category="Pesquisa", year=2026
    )
    create_published_report(
        client, title="Pesquisa 2025", category="Pesquisa", year=2025
    )
    create_published_report(client, title="Estudo 2026", category="Estudo", year=2026)

    response = client.get(REPORTS_URL, params={"year": 2026, "category": "Pesquisa"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Pesquisa 2026"


def test_list_reports_filters_do_not_expose_drafts(client: TestClient):
    create_report(client, year=2026, category="Pesquisa")

    response = client.get(REPORTS_URL, params={"year": 2026, "category": "Pesquisa"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_reports_rejects_invalid_year_filter(client: TestClient):
    response = client.get(REPORTS_URL, params={"year": "abc"})

    assert response.status_code == 422


def test_get_published_report_by_id(client: TestClient):
    published = create_published_report(client)

    response = client.get(f"{REPORTS_URL}/{published['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == published["id"]
    assert response.json()["title"] == VALID_PAYLOAD["title"]


def test_get_draft_report_by_id_is_hidden(client: TestClient):
    draft = create_report(client)

    response = client.get(f"{REPORTS_URL}/{draft['id']}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Relatório não encontrado."


def test_get_nonexistent_report_returns_404(client: TestClient):
    response = client.get(f"{REPORTS_URL}/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_report(client: TestClient):
    report = create_report(client)

    response = client.put(
        f"{REPORTS_URL}/{report['id']}",
        json={
            "title": "Boletim 2026 revisado",
            "description": None,
            "category": "Estudo",
            "year": 2025,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == report["id"]
    assert data["title"] == "Boletim 2026 revisado"
    assert data["description"] is None
    assert data["category"] == "Estudo"
    assert data["year"] == 2025
    assert data["status"] == "draft"


def test_update_report_keeps_publication_status(client: TestClient):
    published = create_published_report(client)

    response = client.put(
        f"{REPORTS_URL}/{published['id']}",
        json={**VALID_PAYLOAD, "title": "Título atualizado"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "published"
    assert response.json()["published_at"] == published["published_at"]


def test_update_report_rejects_invalid_metadata(client: TestClient):
    report = create_report(client)

    response = client.put(
        f"{REPORTS_URL}/{report['id']}",
        json={**VALID_PAYLOAD, "title": "ab"},
    )

    assert response.status_code == 422


def test_update_nonexistent_report_returns_404(client: TestClient):
    response = client.put(f"{REPORTS_URL}/9999", json=VALID_PAYLOAD)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_report(client: TestClient):
    published = create_published_report(client)

    response = client.delete(f"{REPORTS_URL}/{published['id']}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert client.get(f"{REPORTS_URL}/{published['id']}").status_code == 404
    assert client.get(REPORTS_URL).json() == []


def test_delete_nonexistent_report_returns_404(client: TestClient):
    response = client.delete(f"{REPORTS_URL}/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_publish_report(client: TestClient):
    report = create_report(client)

    response = client.patch(f"{REPORTS_URL}/{report['id']}/publish")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "published"
    assert data["published_at"] is not None


def test_publish_report_is_idempotent(client: TestClient):
    first = create_published_report(client)

    response = client.patch(f"{REPORTS_URL}/{first['id']}/publish")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "published"
    assert response.json()["published_at"] == first["published_at"]


def test_publish_nonexistent_report_returns_404(client: TestClient):
    response = client.patch(f"{REPORTS_URL}/9999/publish")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unpublish_report(client: TestClient):
    published = create_published_report(client)

    response = client.patch(f"{REPORTS_URL}/{published['id']}/unpublish")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "draft"
    assert data["published_at"] is None
    assert client.get(REPORTS_URL).json() == []
    assert client.get(f"{REPORTS_URL}/{published['id']}").status_code == 404


def test_unpublish_nonexistent_report_returns_404(client: TestClient):
    response = client.patch(f"{REPORTS_URL}/9999/unpublish")

    assert response.status_code == status.HTTP_404_NOT_FOUND
