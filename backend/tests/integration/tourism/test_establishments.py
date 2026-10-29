import pytest
from fastapi import status
from fastapi.testclient import TestClient

PUBLIC_BASE_URL = "/api/v1/tourism/establishments"
ADMIN_BASE_URL = "/api/v1/admin/tourism/establishments"
NOT_FOUND_DETAIL = "Estabelecimento turístico não encontrado."


def create_establishment(
    client: TestClient,
    name: str = "Hotel Serra Verde",
    category: str = "hotel",
) -> dict:
    response = client.post(
        ADMIN_BASE_URL,
        json={"name": name, "category": category},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def test_create_establishment(client: TestClient) -> None:
    response = client.post(
        ADMIN_BASE_URL,
        json={"name": "Hotel Serra Verde", "category": "hotel"},
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == "Hotel Serra Verde"
    assert data["category"] == "hotel"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_public_establishments(client: TestClient) -> None:
    create_establishment(client, "Hotel Serra Verde", "hotel")
    create_establishment(client, "Pousada Mantiqueira", "pousada")

    response = client.get(PUBLIC_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert [item["name"] for item in response.json()] == [
        "Hotel Serra Verde",
        "Pousada Mantiqueira",
    ]


def test_filter_public_establishments_by_category(client: TestClient) -> None:
    create_establishment(client, "Hotel Serra Verde", "hotel")
    create_establishment(client, "Pousada Mantiqueira", "pousada")

    response = client.get(PUBLIC_BASE_URL, params={"category": "hotel"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Hotel Serra Verde"


def test_get_public_establishment(client: TestClient) -> None:
    establishment = create_establishment(client)

    response = client.get(f"{PUBLIC_BASE_URL}/{establishment['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == establishment["id"]


@pytest.mark.parametrize("base_url", [PUBLIC_BASE_URL, ADMIN_BASE_URL])
def test_get_nonexistent_establishment_returns_404(
    client: TestClient,
    base_url: str,
) -> None:
    response = client.get(f"{base_url}/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_update_establishment(client: TestClient) -> None:
    establishment = create_establishment(client)

    response = client.put(
        f"{ADMIN_BASE_URL}/{establishment['id']}",
        json={
            "name": "Hotel Serra Azul",
            "category": "resort",
            "is_active": True,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Hotel Serra Azul"
    assert response.json()["category"] == "resort"
    assert response.json()["is_active"] is True


def test_update_establishment_with_empty_body_keeps_values(
    client: TestClient,
) -> None:
    establishment = create_establishment(client)

    response = client.put(
        f"{ADMIN_BASE_URL}/{establishment['id']}",
        json={},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == establishment["name"]
    assert response.json()["category"] == establishment["category"]
    assert response.json()["is_active"] is establishment["is_active"]


@pytest.mark.parametrize("field", ["name", "category", "is_active"])
def test_update_establishment_rejects_explicit_null(
    client: TestClient,
    field: str,
) -> None:
    establishment = create_establishment(client)

    response = client.put(
        f"{ADMIN_BASE_URL}/{establishment['id']}",
        json={field: None},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_deactivate_establishment_hides_it_from_public_routes(
    client: TestClient,
) -> None:
    establishment = create_establishment(client)

    response = client.delete(f"{ADMIN_BASE_URL}/{establishment['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    public_response = client.get(f"{PUBLIC_BASE_URL}/{establishment['id']}")
    admin_response = client.get(f"{ADMIN_BASE_URL}/{establishment['id']}")
    assert public_response.status_code == status.HTTP_404_NOT_FOUND
    assert public_response.json() == {"detail": NOT_FOUND_DETAIL}
    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.json()["is_active"] is False


def test_public_list_ignores_inactive_establishments(client: TestClient) -> None:
    active = create_establishment(client, "Hotel Ativo")
    inactive = create_establishment(client, "Hotel Inativo")
    client.delete(f"{ADMIN_BASE_URL}/{inactive['id']}")

    response = client.get(PUBLIC_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [active["id"]]


def test_admin_list_includes_and_filters_inactive_establishments(
    client: TestClient,
) -> None:
    active = create_establishment(client, "Hotel Ativo")
    inactive = create_establishment(client, "Hotel Inativo")
    client.delete(f"{ADMIN_BASE_URL}/{inactive['id']}")

    all_response = client.get(ADMIN_BASE_URL)
    inactive_response = client.get(
        ADMIN_BASE_URL,
        params={"is_active": False, "category": "hotel"},
    )
    assert all_response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in all_response.json()] == [
        active["id"],
        inactive["id"],
    ]
    assert inactive_response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in inactive_response.json()] == [inactive["id"]]


def test_create_establishment_with_invalid_data_returns_422(
    client: TestClient,
) -> None:
    response = client.post(
        ADMIN_BASE_URL,
        json={"name": "", "category": "hotel"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
