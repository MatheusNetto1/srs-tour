from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.indicators.models import Indicator, IndicatorStatus

BASE_URL = "/api/v1/indicators"
ADMIN_URL = "/api/v1/admin/indicators"

NOT_FOUND_DETAIL = "Indicador não encontrado."
ALREADY_EXISTS_DETAIL = "Já existe um indicador com este slug e período."

FIELD_LIMITS = {
    "name": 255,
    "sector": 100,
    "unit": 50,
}
TEXT_FIELDS = list(FIELD_LIMITS)
EDITABLE_FIELDS = [*TEXT_FIELDS, "period", "value"]


def payload(**overrides) -> dict:
    data = {
        "name": "Ocupação Hoteleira",
        "sector": "Hospedagem",
        "period": 2026,
        "value": 75.5,
        "unit": "%",
    }
    data.update(overrides)

    return data


def create_indicator(client: TestClient, **overrides) -> dict:
    response = client.post(ADMIN_URL, json=payload(**overrides))

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def create_published(client: TestClient, **overrides) -> dict:
    indicator = create_indicator(client, **overrides)
    response = client.patch(f"{ADMIN_URL}/{indicator['id']}/publish")

    assert response.status_code == status.HTTP_200_OK

    return response.json()


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def ids(response) -> list[int]:
    return [item["id"] for item in response.json()]


# --------------------------------------------------------------------------
# Criação
# --------------------------------------------------------------------------


def test_create_indicator_always_starts_as_draft(client: TestClient) -> None:
    response = client.post(ADMIN_URL, json=payload())

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Ocupação Hoteleira"
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.parametrize("status_value", ["draft", "published", None])
def test_create_rejects_status_in_payload(
    client: TestClient,
    status_value,
) -> None:
    response = client.post(ADMIN_URL, json=payload(status=status_value))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_rejects_server_controlled_fields(client: TestClient) -> None:
    response = client.post(ADMIN_URL, json=payload(id=999))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_validate_mandatory_fields(client: TestClient) -> None:
    response = client.post(ADMIN_URL, json={"name": "Incompleto"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("field", TEXT_FIELDS)
@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_create_rejects_blank_text(client: TestClient, field, blank) -> None:
    response = client.post(ADMIN_URL, json=payload(**{field: blank}))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("field", TEXT_FIELDS)
def test_create_strips_text(client: TestClient, field) -> None:
    response = client.post(ADMIN_URL, json=payload(**{field: "  Valor  "}))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[field] == "Valor"


@pytest.mark.parametrize(("field", "limit"), FIELD_LIMITS.items())
def test_create_accepts_maximum_length(
    client: TestClient,
    field: str,
    limit: int,
) -> None:
    response = client.post(ADMIN_URL, json=payload(**{field: "x" * limit}))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()[field] == "x" * limit


@pytest.mark.parametrize(("field", "limit"), FIELD_LIMITS.items())
def test_create_rejects_above_maximum_length(
    client: TestClient,
    field: str,
    limit: int,
) -> None:
    response = client.post(ADMIN_URL, json=payload(**{field: "x" * (limit + 1)}))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("value", [75.5, 0, 0.0, -12.5, -1])
def test_create_accepts_positive_zero_and_negative_values(
    client: TestClient,
    value: float,
) -> None:
    response = client.post(ADMIN_URL, json=payload(value=value))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["value"] == value


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity", "1e999"])
def test_create_rejects_non_finite_values(client: TestClient, literal: str) -> None:
    body = (
        '{"name": "n", "sector": "s", "period": 2026, '
        f'"value": {literal}, "unit": "%"}}'
    )

    response = client.post(
        ADMIN_URL,
        content=body,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["loc"] == ["body", "value"]


def test_create_rejects_non_numeric_value(client: TestClient) -> None:
    response = client.post(ADMIN_URL, json=payload(value="abc"))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_rejects_non_numeric_period(client: TestClient) -> None:
    response = client.post(ADMIN_URL, json=payload(period="abc"))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("period", [1900, 2100])
def test_create_accepts_period_boundaries(client: TestClient, period: int) -> None:
    response = client.post(ADMIN_URL, json=payload(period=period))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["period"] == period


@pytest.mark.parametrize("period", [1899, 2101])
def test_create_rejects_period_out_of_bounds(client: TestClient, period: int) -> None:
    response = client.post(ADMIN_URL, json=payload(period=period))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --------------------------------------------------------------------------
# Slug
# --------------------------------------------------------------------------


def test_create_derives_slug_from_name(client: TestClient) -> None:
    response = create_indicator(client, name="Meios de Hospedagem")

    assert response["slug"] == "meios-de-hospedagem"


def test_create_accepts_explicit_slug(client: TestClient) -> None:
    response = create_indicator(client, slug="serie-explicita")

    assert response["slug"] == "serie-explicita"


@pytest.mark.parametrize(
    "slug",
    [
        "Com Espaco",
        "MAIUSCULO",
        "com_underscore",
        "-inicia-com-hifen",
        "termina-com-hifen-",
    ],
)
def test_create_rejects_invalid_slug_format(client: TestClient, slug: str) -> None:
    response = client.post(ADMIN_URL, json=payload(slug=slug))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_accepts_maximum_slug_length(client: TestClient) -> None:
    response = create_indicator(client, slug="a" * 100)

    assert response["slug"] == "a" * 100


def test_create_rejects_slug_above_maximum_length(client: TestClient) -> None:
    response = client.post(ADMIN_URL, json=payload(slug="a" * 101))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_same_slug_different_period_is_allowed(client: TestClient) -> None:
    first = create_indicator(client, slug="serie-x", period=2025)
    second = create_indicator(client, slug="serie-x", period=2026)

    assert first["id"] != second["id"]
    assert first["slug"] == second["slug"] == "serie-x"


def test_create_duplicate_explicit_slug_and_period_is_rejected(
    client: TestClient,
) -> None:
    create_indicator(client, slug="serie-x", period=2026)
    response = client.post(
        ADMIN_URL,
        json=payload(name="Outro nome", slug="serie-x", period=2026),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": ALREADY_EXISTS_DETAIL}


def test_create_duplicate_derived_slug_and_period_is_rejected(
    client: TestClient,
) -> None:
    create_indicator(client, name="Ocupação Hoteleira", period=2026)
    response = client.post(
        ADMIN_URL,
        json=payload(name="Ocupação Hoteleira", period=2026),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": ALREADY_EXISTS_DETAIL}


def test_update_slug_is_immutable(client: TestClient) -> None:
    created = create_indicator(client, name="Meios de Hospedagem")

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=payload(name="Meios de Hospedagem", slug="outro-slug"),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        client.get(f"{ADMIN_URL}/{created['id']}").json()["slug"]
        == "meios-de-hospedagem"
    )


def test_update_period_conflicting_with_another_series_is_rejected(
    client: TestClient,
) -> None:
    create_indicator(client, slug="serie-a", period=2025)
    other = create_indicator(client, slug="serie-a", period=2026)

    response = client.put(
        f"{ADMIN_URL}/{other['id']}",
        json=payload(period=2025),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": ALREADY_EXISTS_DETAIL}


def test_update_period_to_a_free_value_succeeds_and_keeps_slug(
    client: TestClient,
) -> None:
    created = create_indicator(client, slug="serie-a", period=2026)

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=payload(name=created["name"], period=2027),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["slug"] == "serie-a"
    assert response.json()["period"] == 2027


# --------------------------------------------------------------------------
# Leitura pública: somente PUBLISHED
# --------------------------------------------------------------------------


def test_public_list_never_returns_drafts(client: TestClient) -> None:
    create_indicator(client, name="Rascunho")

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_public_list_returns_only_published(client: TestClient) -> None:
    create_indicator(client, name="Rascunho")
    published = create_published(client, name="Publicado")

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [published["id"]]
    assert all(item["status"] == "published" for item in response.json())


@pytest.mark.parametrize("status_value", ["draft", "published", "XYZ"])
def test_public_list_cannot_be_bypassed_with_status_parameter(
    client: TestClient,
    status_value: str,
) -> None:
    create_indicator(client, name="Rascunho")
    published = create_published(client, name="Publicado")

    response = client.get(BASE_URL, params={"status": status_value})

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [published["id"]]


def test_public_get_by_id_returns_published(client: TestClient) -> None:
    published = create_published(client)

    response = client.get(f"{BASE_URL}/{published['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == published["id"]
    assert response.json()["status"] == "published"


def test_public_get_by_id_of_draft_returns_not_found(client: TestClient) -> None:
    draft = create_indicator(client)

    response = client.get(f"{BASE_URL}/{draft['id']}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_public_get_by_id_after_unpublish_returns_not_found(
    client: TestClient,
) -> None:
    published = create_published(client)
    client.patch(f"{ADMIN_URL}/{published['id']}/unpublish")

    response = client.get(f"{BASE_URL}/{published['id']}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_public_get_nonexistent_returns_not_found_in_portuguese(
    client: TestClient,
) -> None:
    response = client.get(f"{BASE_URL}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_public_get_with_invalid_id_returns_validation_error(
    client: TestClient,
) -> None:
    response = client.get(f"{BASE_URL}/abc")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --------------------------------------------------------------------------
# Filtros e ordenação (leitura pública)
# --------------------------------------------------------------------------


def seed_published(client: TestClient) -> dict[str, dict]:
    return {
        "hotels_2026": create_published(
            client,
            name="Ocupação Hoteleira",
            sector="Hospedagem",
            period=2026,
        ),
        "hotels_2025": create_published(
            client,
            name="Ocupação 2025",
            sector="Hospedagem",
            period=2025,
        ),
        "transport_2025": create_published(
            client,
            name="Chegadas",
            sector="Transporte",
            period=2025,
        ),
    }


def test_filter_by_period(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(BASE_URL, params={"period": 2025})

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [
        seeded["hotels_2025"]["id"],
        seeded["transport_2025"]["id"],
    ]


def test_filter_by_sector(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(BASE_URL, params={"sector": "Hospedagem"})

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [
        seeded["hotels_2026"]["id"],
        seeded["hotels_2025"]["id"],
    ]


def test_filter_by_period_and_sector(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(
        BASE_URL,
        params={"period": 2025, "sector": "Transporte"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [seeded["transport_2025"]["id"]]
    assert response.json()[0]["name"] == "Chegadas"


def test_filter_by_period_range(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(
        BASE_URL,
        params={"period_from": 2025, "period_to": 2025},
    )

    assert response.status_code == status.HTTP_200_OK
    assert set(ids(response)) == {
        seeded["hotels_2025"]["id"],
        seeded["transport_2025"]["id"],
    }


def test_filter_by_period_range_and_slug(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(
        BASE_URL,
        params={
            "period_from": 2024,
            "period_to": 2025,
            "slug": seeded["hotels_2025"]["slug"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [seeded["hotels_2025"]["id"]]


@pytest.mark.parametrize("base_url", [BASE_URL, ADMIN_URL])
def test_filter_period_from_greater_than_period_to_returns_422(
    client: TestClient,
    base_url: str,
) -> None:
    response = client.get(
        base_url,
        params={"period_from": 2026, "period_to": 2025},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_filter_by_slug(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(BASE_URL, params={"slug": seeded["hotels_2026"]["slug"]})

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [seeded["hotels_2026"]["id"]]


def test_filter_without_matches_returns_empty_list(client: TestClient) -> None:
    seed_published(client)

    response = client.get(BASE_URL, params={"period": 1999})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_filters_do_not_expose_drafts(client: TestClient) -> None:
    create_indicator(client, name="Rascunho", period=2026, sector="Hospedagem")
    published = create_published(
        client,
        name="Publicado",
        period=2026,
        sector="Hospedagem",
    )

    response = client.get(
        BASE_URL,
        params={"period": 2026, "sector": "Hospedagem"},
    )

    assert ids(response) == [published["id"]]


def test_list_order_is_deterministic_by_id(client: TestClient) -> None:
    first = create_published(client, name="C")
    second = create_published(client, name="A")
    third = create_published(client, name="B")

    expected = [first["id"], second["id"], third["id"]]

    assert ids(client.get(BASE_URL)) == expected
    assert ids(client.get(BASE_URL)) == expected


def test_list_order_stays_stable_after_updates(client: TestClient) -> None:
    first = create_published(client, name="Primeiro")
    second = create_published(client, name="Segundo")

    client.put(
        f"{ADMIN_URL}/{first['id']}",
        json=payload(name="Primeiro editado"),
    )

    assert ids(client.get(BASE_URL)) == [first["id"], second["id"]]


# --------------------------------------------------------------------------
# Último valor publicado (/latest)
# --------------------------------------------------------------------------


def test_latest_endpoint_returns_200_with_empty_database(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/latest")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_latest_returns_one_row_per_slug_with_the_highest_period(
    client: TestClient,
) -> None:
    create_published(client, name="Meios de hospedagem", period=2024)
    newest = create_published(client, name="Meios de hospedagem", period=2026)
    create_published(client, name="Meios de hospedagem", period=2025)
    other_series = create_published(client, name="Empregos no turismo", period=2026)

    response = client.get(f"{BASE_URL}/latest")

    assert response.status_code == status.HTTP_200_OK
    assert set(ids(response)) == {newest["id"], other_series["id"]}


def test_latest_ignores_drafts(client: TestClient) -> None:
    create_indicator(client, name="Rascunho", period=2026)

    response = client.get(f"{BASE_URL}/latest")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_latest_falls_back_to_the_highest_published_period_when_newest_is_draft(
    client: TestClient,
) -> None:
    published = create_published(client, name="Meios de hospedagem", period=2025)
    create_indicator(client, name="Meios de hospedagem", period=2026)

    response = client.get(f"{BASE_URL}/latest")

    assert ids(response) == [published["id"]]


def test_latest_filters_by_sector(client: TestClient) -> None:
    seeded = seed_published(client)

    response = client.get(f"{BASE_URL}/latest", params={"sector": "Transporte"})

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [seeded["transport_2025"]["id"]]


def test_numeric_id_still_works_alongside_the_latest_route(
    client: TestClient,
) -> None:
    published = create_published(client)

    response = client.get(f"{BASE_URL}/{published['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == published["id"]


# --------------------------------------------------------------------------
# Leitura administrativa
# --------------------------------------------------------------------------


def test_admin_list_returns_drafts_and_published(client: TestClient) -> None:
    draft = create_indicator(client, name="Rascunho")
    published = create_published(client, name="Publicado")

    response = client.get(ADMIN_URL)

    assert response.status_code == status.HTTP_200_OK
    assert ids(response) == [draft["id"], published["id"]]


@pytest.mark.parametrize(
    ("status_value", "expected_name"),
    [("draft", "Rascunho"), ("published", "Publicado")],
)
def test_admin_list_filters_by_status(
    client: TestClient,
    status_value: str,
    expected_name: str,
) -> None:
    create_indicator(client, name="Rascunho")
    create_published(client, name="Publicado")

    response = client.get(ADMIN_URL, params={"status": status_value})

    assert response.status_code == status.HTTP_200_OK
    assert [item["name"] for item in response.json()] == [expected_name]


def test_admin_list_filters_by_period_and_sector(client: TestClient) -> None:
    create_indicator(client, period=2025, sector="Transporte")
    target = create_indicator(client, period=2026, sector="Hospedagem")

    response = client.get(
        ADMIN_URL,
        params={"period": 2026, "sector": "Hospedagem"},
    )

    assert ids(response) == [target["id"]]


def test_admin_list_rejects_invalid_status(client: TestClient) -> None:
    response = client.get(ADMIN_URL, params={"status": "XYZ"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_admin_get_returns_draft(client: TestClient) -> None:
    draft = create_indicator(client)

    response = client.get(f"{ADMIN_URL}/{draft['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "draft"


def test_admin_get_nonexistent_returns_not_found(client: TestClient) -> None:
    response = client.get(f"{ADMIN_URL}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


# --------------------------------------------------------------------------
# Atualização (PUT completo)
# --------------------------------------------------------------------------


def test_update_indicator_replaces_all_editable_fields(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]
    new_data = {
        "name": "Chegadas",
        "sector": "Transporte",
        "period": 2025,
        "value": -3.5,
        "unit": "mil",
    }

    response = client.put(f"{ADMIN_URL}/{indicator_id}", json=new_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert {key: data[key] for key in new_data} == new_data
    assert data["id"] == indicator_id
    assert data["status"] == "draft"


def test_update_strips_text(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    response = client.put(
        f"{ADMIN_URL}/{indicator_id}",
        json=payload(name="  Novo nome  "),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Novo nome"


def test_update_does_not_change_status(client: TestClient) -> None:
    published = create_published(client)

    response = client.put(
        f"{ADMIN_URL}/{published['id']}",
        json=payload(name="Editado"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "published"


def test_update_refreshes_updated_at_and_keeps_created_at(
    client: TestClient,
) -> None:
    created = create_indicator(client)

    response = client.put(
        f"{ADMIN_URL}/{created['id']}",
        json=payload(value=80.0),
    )

    updated = response.json()

    assert updated["created_at"] == created["created_at"]
    assert parse_datetime(updated["updated_at"]) > parse_datetime(created["updated_at"])


def test_update_rejects_empty_body(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    response = client.put(f"{ADMIN_URL}/{indicator_id}", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("field", EDITABLE_FIELDS)
def test_update_rejects_null_in_required_field(client: TestClient, field) -> None:
    indicator_id = create_indicator(client)["id"]

    response = client.put(
        f"{ADMIN_URL}/{indicator_id}",
        json=payload(**{field: None}),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("field", EDITABLE_FIELDS)
def test_update_rejects_partial_payload(client: TestClient, field) -> None:
    indicator_id = create_indicator(client)["id"]
    partial = payload()
    del partial[field]

    response = client.put(f"{ADMIN_URL}/{indicator_id}", json=partial)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("status_value", ["draft", "published"])
def test_update_cannot_change_status(
    client: TestClient,
    status_value: str,
) -> None:
    indicator_id = create_indicator(client)["id"]

    response = client.put(
        f"{ADMIN_URL}/{indicator_id}",
        json=payload(status=status_value),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert client.get(f"{ADMIN_URL}/{indicator_id}").json()["status"] == "draft"


@pytest.mark.parametrize("extra", ["id", "created_at", "updated_at"])
def test_update_rejects_server_controlled_fields(client: TestClient, extra) -> None:
    indicator_id = create_indicator(client)["id"]

    response = client.put(
        f"{ADMIN_URL}/{indicator_id}",
        json=payload(**{extra: 1}),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_rejects_invalid_values(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    for invalid in [
        payload(name="   "),
        payload(unit="x" * 51),
        payload(value="abc"),
        payload(period=1800),
    ]:
        response = client.put(f"{ADMIN_URL}/{indicator_id}", json=invalid)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_nonexistent_returns_not_found(client: TestClient) -> None:
    response = client.put(f"{ADMIN_URL}/999999", json=payload())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


# --------------------------------------------------------------------------
# Publish / unpublish
# --------------------------------------------------------------------------


def test_publish_and_unpublish(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    publish = client.patch(f"{ADMIN_URL}/{indicator_id}/publish")

    assert publish.status_code == status.HTTP_200_OK
    assert publish.json()["status"] == "published"
    assert ids(client.get(BASE_URL)) == [indicator_id]

    unpublish = client.patch(f"{ADMIN_URL}/{indicator_id}/unpublish")

    assert unpublish.status_code == status.HTTP_200_OK
    assert unpublish.json()["status"] == "draft"
    assert client.get(BASE_URL).json() == []


def test_publish_is_idempotent(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    first = client.patch(f"{ADMIN_URL}/{indicator_id}/publish")
    second = client.patch(f"{ADMIN_URL}/{indicator_id}/publish")

    assert first.status_code == status.HTTP_200_OK
    assert second.status_code == status.HTTP_200_OK
    assert second.json()["status"] == "published"
    assert second.json()["updated_at"] == first.json()["updated_at"]


def test_unpublish_is_idempotent(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    first = client.patch(f"{ADMIN_URL}/{indicator_id}/unpublish")
    second = client.patch(f"{ADMIN_URL}/{indicator_id}/unpublish")

    assert first.status_code == status.HTTP_200_OK
    assert second.status_code == status.HTTP_200_OK
    assert second.json()["status"] == "draft"
    assert second.json()["updated_at"] == first.json()["updated_at"]


@pytest.mark.parametrize("action", ["publish", "unpublish"])
def test_status_change_of_nonexistent_returns_not_found(
    client: TestClient,
    action: str,
) -> None:
    response = client.patch(f"{ADMIN_URL}/999999/{action}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


# --------------------------------------------------------------------------
# Remoção (física)
# --------------------------------------------------------------------------


def test_delete_indicator(client: TestClient, db_session: Session) -> None:
    indicator_id = create_published(client)["id"]

    response = client.delete(f"{ADMIN_URL}/{indicator_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert (
        client.get(f"{ADMIN_URL}/{indicator_id}").status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert (
        client.get(f"{BASE_URL}/{indicator_id}").status_code
        == status.HTTP_404_NOT_FOUND
    )

    db_session.expire_all()

    assert db_session.get(Indicator, indicator_id) is None


def test_delete_nonexistent_returns_not_found(client: TestClient) -> None:
    response = client.delete(f"{ADMIN_URL}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_delete_twice_returns_not_found_on_second_call(client: TestClient) -> None:
    indicator_id = create_indicator(client)["id"]

    first = client.delete(f"{ADMIN_URL}/{indicator_id}")
    second = client.delete(f"{ADMIN_URL}/{indicator_id}")

    assert first.status_code == status.HTTP_204_NO_CONTENT
    assert second.status_code == status.HTTP_404_NOT_FOUND


# --------------------------------------------------------------------------
# Contrato de rotas
# --------------------------------------------------------------------------

EXPECTED_ROUTES = {
    ("GET", "/api/v1/indicators"),
    ("GET", "/api/v1/indicators/latest"),
    ("GET", "/api/v1/indicators/{indicator_id}"),
    ("GET", "/api/v1/admin/indicators"),
    ("GET", "/api/v1/admin/indicators/{indicator_id}"),
    ("POST", "/api/v1/admin/indicators"),
    ("PUT", "/api/v1/admin/indicators/{indicator_id}"),
    ("DELETE", "/api/v1/admin/indicators/{indicator_id}"),
    ("PATCH", "/api/v1/admin/indicators/{indicator_id}/publish"),
    ("PATCH", "/api/v1/admin/indicators/{indicator_id}/unpublish"),
}


def test_registered_indicator_routes_match_the_contract(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == status.HTTP_200_OK

    registered = {
        (method.upper(), path)
        for path, operations in response.json()["paths"].items()
        if "indicators" in path
        for method in operations
    }

    assert registered == EXPECTED_ROUTES


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
def test_write_operations_are_not_available_on_the_public_path(
    client: TestClient,
    method: str,
    path: str,
    expected_status: int,
) -> None:
    response = client.request(method, path, json=payload())

    assert response.status_code == expected_status
    assert client.get(ADMIN_URL).json() == []


def test_old_admin_read_path_is_not_an_administrative_route(
    client: TestClient,
) -> None:
    create_indicator(client, name="Rascunho")

    response = client.get(f"{BASE_URL}/admin")

    # "admin" é tratado como um indicator_id público inválido, nunca como leitura
    # administrativa de rascunhos.
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Rascunho" not in response.text


# --------------------------------------------------------------------------
# Serialização de dados persistidos
# --------------------------------------------------------------------------


def insert_published_row(
    db_session: Session,
    name: str,
    slug: str,
    period: int = 2026,
) -> int:
    indicator_id = db_session.scalar(
        text(
            "INSERT INTO indicators (name, slug, sector, period, value, unit, status) "
            "VALUES (:name, :slug, 'Hospedagem', :period, 1, '%', 'published') "
            "RETURNING id"
        ),
        {"name": name, "slug": slug, "period": period},
    )
    db_session.commit()

    return indicator_id


def test_responses_serialize_persisted_rows_that_violate_input_rules(
    client: TestClient,
    db_session: Session,
) -> None:
    empty_id = insert_published_row(db_session, "", slug="raw-empty")
    padded_id = insert_published_row(db_session, "  Espaços  ", slug="raw-padded")

    public_list = client.get(BASE_URL)
    public_get = client.get(f"{BASE_URL}/{padded_id}")
    admin_get = client.get(f"{ADMIN_URL}/{empty_id}")

    assert public_list.status_code == status.HTTP_200_OK
    assert [item["name"] for item in public_list.json()] == ["", "  Espaços  "]
    assert public_get.status_code == status.HTTP_200_OK
    assert public_get.json()["name"] == "  Espaços  "
    assert admin_get.status_code == status.HTTP_200_OK
    assert admin_get.json()["name"] == ""


# --------------------------------------------------------------------------
# Banco de dados e mapeamento ORM
# --------------------------------------------------------------------------


def test_indicators_table_is_empty_at_test_start(db_session: Session) -> None:
    count = db_session.scalar(select(func.count()).select_from(Indicator))

    assert count == 0


def test_orm_returns_status_as_indicator_status(
    client: TestClient,
    db_session: Session,
) -> None:
    indicator_id = create_published(client)["id"]

    db_session.expire_all()
    indicator = db_session.get(Indicator, indicator_id)

    assert indicator is not None
    assert isinstance(indicator.status, IndicatorStatus)
    assert indicator.status is IndicatorStatus.PUBLISHED


def test_status_is_persisted_as_plain_string(
    client: TestClient,
    db_session: Session,
) -> None:
    indicator_id = create_published(client)["id"]

    stored_status = db_session.scalar(
        text("SELECT status FROM indicators WHERE id = :id"),
        {"id": indicator_id},
    )

    assert stored_status == "published"


def test_period_is_persisted_as_integer(
    client: TestClient,
    db_session: Session,
) -> None:
    indicator_id = create_indicator(client, period=2026)["id"]

    stored_period = db_session.scalar(
        text("SELECT period FROM indicators WHERE id = :id"),
        {"id": indicator_id},
    )

    assert stored_period == 2026
    assert isinstance(stored_period, int)


def test_indicators_status_does_not_use_a_native_enum_type(
    db_session: Session,
) -> None:
    status_enum_types = db_session.scalar(
        text("SELECT count(*) FROM pg_type WHERE typname = 'indicatorstatus'")
    )

    assert status_enum_types == 0


def test_database_has_a_single_status_check_constraint(db_session: Session) -> None:
    constraints = db_session.scalars(
        text(
            "SELECT conname FROM pg_constraint "
            "WHERE conrelid = 'indicators'::regclass AND contype = 'c'"
        )
    ).all()

    assert constraints == ["ck_indicators_status"]


def test_database_has_a_slug_period_unique_constraint(db_session: Session) -> None:
    constraints = db_session.scalars(
        text(
            "SELECT conname FROM pg_constraint "
            "WHERE conrelid = 'indicators'::regclass AND contype = 'u'"
        )
    ).all()

    assert constraints == ["uq_indicators_slug_period"]


def test_database_rejects_invalid_status(db_session: Session) -> None:
    insert = text(
        "INSERT INTO indicators (name, slug, sector, period, value, unit, status) "
        "VALUES ('n', 'slug-invalid-status', 's', 2026, 1, '%', :status)"
    )

    with pytest.raises(IntegrityError) as error:
        db_session.execute(insert, {"status": "ARCHIVED"})
        db_session.commit()

    db_session.rollback()

    assert "ck_indicators_status" in str(error.value.orig)


def test_database_rejects_duplicate_slug_and_period(db_session: Session) -> None:
    insert_published_row(db_session, "Primeiro", slug="slug-duplicado", period=2026)

    with pytest.raises(IntegrityError) as error:
        db_session.execute(
            text(
                "INSERT INTO indicators "
                "(name, slug, sector, period, value, unit, status) "
                "VALUES ('Segundo', 'slug-duplicado', 's', 2026, 1, '%', 'draft')"
            )
        )
        db_session.commit()

    db_session.rollback()

    assert "uq_indicators_slug_period" in str(error.value.orig)


def test_database_fills_timestamps_by_default(db_session: Session) -> None:
    db_session.execute(
        text(
            "INSERT INTO indicators (name, slug, sector, period, value, unit, status) "
            "VALUES ('n', 'slug-timestamps', 's', 2026, 1, '%', 'draft')"
        )
    )
    db_session.commit()

    row = db_session.execute(
        text(
            "SELECT created_at, updated_at FROM indicators "
            "WHERE slug = 'slug-timestamps'"
        )
    ).one()

    assert row.created_at is not None
    assert row.updated_at is not None
