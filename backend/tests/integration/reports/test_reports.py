import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.reports import service
from app.reports.models import Report, ReportStatus
from app.reports.schemas import ReportCreate

BASE_URL = "/api/v1/reports"
ADMIN_URL = "/api/v1/admin/reports"

NOT_FOUND_RESPONSE = {
    "detail": "Relatório não encontrado.",
    "code": "report.not_found",
}

VALID_PAYLOAD = {
    "title": "Boletim 2026",
    "description": "Boletim trimestral do Observatório",
    "category": "Pesquisa",
    "year": 2026,
}


def create_report(client: TestClient, **overrides) -> dict:
    response = client.post(ADMIN_URL, json={**VALID_PAYLOAD, **overrides})

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def create_published_report(client: TestClient, **overrides) -> dict:
    report = create_report(client, **overrides)
    response = client.patch(f"{ADMIN_URL}/{report['id']}/publish")

    assert response.status_code == status.HTTP_200_OK

    return response.json()


def test_create_report_starts_as_draft_and_persists(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        ADMIN_URL,
        json={
            **VALID_PAYLOAD,
            "title": "  Boletim 2026  ",
            "category": "  Pesquisa  ",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["id"] > 0
    assert data["title"] == "Boletim 2026"
    assert data["description"] == VALID_PAYLOAD["description"]
    assert data["category"] == "Pesquisa"
    assert data["year"] == VALID_PAYLOAD["year"]
    assert data["status"] == "draft"
    assert data["published_at"] is None
    assert data["file_path"] is None
    assert data["created_at"]
    assert data["updated_at"]

    db_session.expire_all()
    stored = db_session.get(Report, data["id"])

    assert stored is not None
    assert stored.title == "Boletim 2026"
    assert stored.category == "Pesquisa"
    assert stored.status == ReportStatus.DRAFT.value
    assert stored.published_at is None


def test_create_report_without_description(client: TestClient) -> None:
    payload = {
        key: value for key, value in VALID_PAYLOAD.items() if key != "description"
    }

    response = client.post(ADMIN_URL, json=payload)

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
def test_create_report_rejects_invalid_metadata(
    client: TestClient,
    overrides: dict,
) -> None:
    response = client.post(ADMIN_URL, json={**VALID_PAYLOAD, **overrides})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["code"] == "validation.failed"


@pytest.mark.parametrize("missing_field", ["title", "category", "year"])
def test_create_report_requires_mandatory_fields(
    client: TestClient,
    missing_field: str,
) -> None:
    payload = {
        key: value for key, value in VALID_PAYLOAD.items() if key != missing_field
    }

    response = client.post(ADMIN_URL, json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["code"] == "validation.failed"


def test_create_report_rejects_nul_byte_in_title(client: TestClient) -> None:
    response = client.post(
        ADMIN_URL,
        json={**VALID_PAYLOAD, "title": "Boletim\u00002026"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["code"] == "validation.invalid_value"


def test_list_reports_hides_drafts(client: TestClient) -> None:
    create_report(client)

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_reports_returns_only_published(client: TestClient) -> None:
    create_report(client, title="Rascunho interno")
    published = create_published_report(client, title="Boletim publicado")

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == published["id"]
    assert data[0]["status"] == "published"


def test_list_reports_filters_by_year(client: TestClient) -> None:
    create_published_report(client, title="Boletim 2026", year=2026)
    create_published_report(client, title="Boletim 2025", year=2025)

    response = client.get(BASE_URL, params={"year": 2026})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["year"] == 2026


def test_list_reports_filters_by_category_ignoring_case(client: TestClient) -> None:
    create_published_report(client, title="Pesquisa anual", category="Pesquisa")
    create_published_report(client, title="Estudo setorial", category="Estudo")

    response = client.get(BASE_URL, params={"category": "pesquisa"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Pesquisa"


def test_list_reports_combines_filters(client: TestClient) -> None:
    create_published_report(
        client,
        title="Pesquisa 2026",
        category="Pesquisa",
        year=2026,
    )
    create_published_report(
        client,
        title="Pesquisa 2025",
        category="Pesquisa",
        year=2025,
    )
    create_published_report(client, title="Estudo 2026", category="Estudo", year=2026)

    response = client.get(BASE_URL, params={"year": 2026, "category": "Pesquisa"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Pesquisa 2026"


def test_list_reports_filters_do_not_expose_drafts(client: TestClient) -> None:
    create_report(client, year=2026, category="Pesquisa")

    response = client.get(
        BASE_URL,
        params={"year": 2026, "category": "Pesquisa", "q": "Boletim"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_reports_searches_by_q_across_title_description_and_category(
    client: TestClient,
) -> None:
    by_title = create_published_report(
        client,
        title="Fluxo Aeroviário Regional",
        description=None,
        category="Transporte",
    )
    by_description = create_published_report(
        client,
        title="Anuário Estatístico",
        description="Levantamento sobre gastronomia mineira",
        category="Anuário",
    )
    by_category = create_published_report(
        client,
        title="Indicadores do Setor",
        description="Resumo anual",
        category="Hotelaria",
    )
    create_report(
        client,
        title="Fluxo Aeroviário Rascunho",
        description="gastronomia mineira",
        category="Hotelaria",
    )

    res_title = client.get(BASE_URL, params={"q": "AEROVIÁRIO"})
    assert res_title.status_code == status.HTTP_200_OK
    assert [item["id"] for item in res_title.json()] == [by_title["id"]]

    res_desc = client.get(BASE_URL, params={"q": "GASTRONOMIA"})
    assert res_desc.status_code == status.HTTP_200_OK
    assert [item["id"] for item in res_desc.json()] == [by_description["id"]]

    res_cat = client.get(BASE_URL, params={"q": "hotel"})
    assert res_cat.status_code == status.HTTP_200_OK
    assert [item["id"] for item in res_cat.json()] == [by_category["id"]]


def test_list_reports_search_escapes_like_wildcards(client: TestClient) -> None:
    with_percent = create_published_report(
        client,
        title="Taxa de 100% de ocupação",
        description="Relatório",
        category="Pesquisa",
    )
    with_underscore = create_published_report(
        client,
        title="Indicador_A_2026",
        description="Relatório",
        category="Pesquisa",
    )
    create_published_report(
        client,
        title="Taxa de 1000 de ocupação",
        description="IndicadorXA2026",
        category="Pesquisa",
    )

    res_percent = client.get(BASE_URL, params={"q": "100%"})
    assert res_percent.status_code == status.HTTP_200_OK
    assert [item["id"] for item in res_percent.json()] == [with_percent["id"]]

    res_underscore = client.get(BASE_URL, params={"q": "Indicador_A"})
    assert res_underscore.status_code == status.HTTP_200_OK
    assert [item["id"] for item in res_underscore.json()] == [with_underscore["id"]]


def test_list_reports_combines_q_with_year_and_category(client: TestClient) -> None:
    target = create_published_report(
        client,
        title="Demanda Turística 2026",
        category="Pesquisa",
        year=2026,
    )
    create_published_report(
        client,
        title="Demanda Turística 2025",
        category="Pesquisa",
        year=2025,
    )
    create_published_report(
        client,
        title="Demanda Turística Estudo",
        category="Estudo",
        year=2026,
    )

    response = client.get(
        BASE_URL,
        params={"q": "demanda", "year": 2026, "category": "pesquisa"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [target["id"]]


@pytest.mark.parametrize("invalid_q", ["", "x" * 101])
def test_list_reports_rejects_invalid_q_length(
    client: TestClient,
    invalid_q: str,
) -> None:
    public_res = client.get(BASE_URL, params={"q": invalid_q})
    admin_res = client.get(ADMIN_URL, params={"q": invalid_q})

    assert public_res.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert admin_res.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_reports_rejects_invalid_year_filter(client: TestClient) -> None:
    response = client.get(BASE_URL, params={"year": "abc"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_published_report_by_id(client: TestClient) -> None:
    published = create_published_report(client)

    response = client.get(f"{BASE_URL}/{published['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == published["id"]
    assert response.json()["title"] == VALID_PAYLOAD["title"]


def test_get_draft_report_by_id_is_hidden_on_public_route(client: TestClient) -> None:
    draft = create_report(client)

    response = client.get(f"{BASE_URL}/{draft['id']}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == NOT_FOUND_RESPONSE


def test_get_nonexistent_report_returns_404(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == NOT_FOUND_RESPONSE


def test_get_report_with_id_out_of_int4_range_returns_422(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/99999999999999")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["code"] == "validation.invalid_value"


def test_admin_list_returns_drafts_and_published(client: TestClient) -> None:
    draft = create_report(client, title="Relatório A (rascunho)")
    published = create_published_report(client, title="Relatório B (publicado)")

    response = client.get(ADMIN_URL)

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [draft["id"], published["id"]]


def test_admin_list_filters_by_status_and_q(client: TestClient) -> None:
    draft = create_report(client, title="Diagnóstico Municipal")
    published = create_published_report(client, title="Diagnóstico Estadual")

    draft_res = client.get(ADMIN_URL, params={"status": "draft", "q": "diagnóstico"})
    assert draft_res.status_code == status.HTTP_200_OK
    assert [item["id"] for item in draft_res.json()] == [draft["id"]]

    pub_res = client.get(ADMIN_URL, params={"status": "published", "q": "diagnóstico"})
    assert pub_res.status_code == status.HTTP_200_OK
    assert [item["id"] for item in pub_res.json()] == [published["id"]]


def test_admin_get_report_returns_draft_and_nonexistent_returns_404(
    client: TestClient,
) -> None:
    draft = create_report(client)

    ok_res = client.get(f"{ADMIN_URL}/{draft['id']}")
    assert ok_res.status_code == status.HTTP_200_OK
    assert ok_res.json()["id"] == draft["id"]
    assert ok_res.json()["status"] == "draft"

    missing_res = client.get(f"{ADMIN_URL}/9999")
    assert missing_res.status_code == status.HTTP_404_NOT_FOUND
    assert missing_res.json() == NOT_FOUND_RESPONSE


def test_update_report(client: TestClient, db_session: Session) -> None:
    report = create_report(client)

    response = client.put(
        f"{ADMIN_URL}/{report['id']}",
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

    db_session.expire_all()
    stored = db_session.get(Report, report["id"])

    assert stored is not None
    assert stored.title == "Boletim 2026 revisado"
    assert stored.description is None
    assert stored.category == "Estudo"
    assert stored.year == 2025


def test_update_report_keeps_publication_status(client: TestClient) -> None:
    published = create_published_report(client)

    response = client.put(
        f"{ADMIN_URL}/{published['id']}",
        json={**VALID_PAYLOAD, "title": "Título atualizado"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "published"
    assert response.json()["published_at"] == published["published_at"]


def test_update_report_rejects_invalid_metadata(client: TestClient) -> None:
    report = create_report(client)

    response = client.put(
        f"{ADMIN_URL}/{report['id']}",
        json={**VALID_PAYLOAD, "title": "ab"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_nonexistent_report_returns_404(client: TestClient) -> None:
    response = client.put(f"{ADMIN_URL}/9999", json=VALID_PAYLOAD)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == NOT_FOUND_RESPONSE


def test_delete_report(client: TestClient, db_session: Session) -> None:
    published = create_published_report(client)

    response = client.delete(f"{ADMIN_URL}/{published['id']}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        client.get(f"{BASE_URL}/{published['id']}").status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert (
        client.get(f"{ADMIN_URL}/{published['id']}").status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert client.get(BASE_URL).json() == []

    db_session.expire_all()
    assert db_session.get(Report, published["id"]) is None


def test_delete_nonexistent_report_returns_404(client: TestClient) -> None:
    response = client.delete(f"{ADMIN_URL}/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == NOT_FOUND_RESPONSE


def test_publish_report(client: TestClient, db_session: Session) -> None:
    report = create_report(client)

    response = client.patch(f"{ADMIN_URL}/{report['id']}/publish")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "published"
    assert data["published_at"] is not None

    db_session.expire_all()
    stored = db_session.get(Report, report["id"])

    assert stored is not None
    assert stored.status == ReportStatus.PUBLISHED.value
    assert stored.published_at is not None


def test_publish_report_is_idempotent(client: TestClient) -> None:
    first = create_published_report(client)

    response = client.patch(f"{ADMIN_URL}/{first['id']}/publish")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "published"
    assert response.json()["published_at"] == first["published_at"]


def test_publish_nonexistent_report_returns_404(client: TestClient) -> None:
    response = client.patch(f"{ADMIN_URL}/9999/publish")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == NOT_FOUND_RESPONSE


def test_unpublish_report(client: TestClient, db_session: Session) -> None:
    published = create_published_report(client)

    response = client.patch(f"{ADMIN_URL}/{published['id']}/unpublish")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "draft"
    assert data["published_at"] is None
    assert client.get(BASE_URL).json() == []
    assert (
        client.get(f"{BASE_URL}/{published['id']}").status_code
        == status.HTTP_404_NOT_FOUND
    )

    db_session.expire_all()
    stored = db_session.get(Report, published["id"])

    assert stored is not None
    assert stored.status == ReportStatus.DRAFT.value
    assert stored.published_at is None


def test_unpublish_nonexistent_report_returns_404(client: TestClient) -> None:
    response = client.patch(f"{ADMIN_URL}/9999/unpublish")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == NOT_FOUND_RESPONSE


@pytest.mark.parametrize(
    ("method", "path", "expected_status"),
    [
        ("POST", BASE_URL, status.HTTP_405_METHOD_NOT_ALLOWED),
        ("PUT", f"{BASE_URL}/1", status.HTTP_405_METHOD_NOT_ALLOWED),
        ("DELETE", f"{BASE_URL}/1", status.HTTP_405_METHOD_NOT_ALLOWED),
        ("PATCH", f"{BASE_URL}/1/publish", status.HTTP_404_NOT_FOUND),
        ("PATCH", f"{BASE_URL}/1/unpublish", status.HTTP_404_NOT_FOUND),
    ],
)
def test_write_operations_are_not_available_on_public_reports_router(
    client: TestClient,
    method: str,
    path: str,
    expected_status: int,
) -> None:
    response = client.request(method, path, json=VALID_PAYLOAD)

    assert response.status_code == expected_status
    assert client.get(ADMIN_URL).json() == []


def test_service_create_and_publish_signatures_remain_compatible(
    db_session: Session,
) -> None:
    created = service.create_report(
        db_session,
        ReportCreate(
            title="Relatório Seed",
            description="Gerado via service",
            category="Pesquisa",
            year=2026,
        ),
    )
    published = service.publish_report(db_session, created.id)

    assert isinstance(created, Report)
    assert isinstance(published, Report)
    assert published.status == ReportStatus.PUBLISHED.value
    assert published.published_at is not None
