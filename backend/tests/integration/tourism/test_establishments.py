from fastapi import status
from fastapi.testclient import TestClient

BASE_URL = "/api/v1/tourism/establishments"


def create_establishment(
    client: TestClient,
    name: str = "Hotel Serra Verde",
    category: str = "hotel",
) -> dict:
    response = client.post(
        BASE_URL,
        json={
            "name": name,
            "category": category,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def test_create_establishment(client: TestClient) -> None:
    response = client.post(
        BASE_URL,
        json={
            "name": "Hotel Serra Verde",
            "category": "hotel",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Hotel Serra Verde"
    assert data["category"] == "hotel"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_establishments(client: TestClient) -> None:
    create_establishment(client, "Hotel Serra Verde", "hotel")
    create_establishment(client, "Pousada Mantiqueira", "pousada")

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Hotel Serra Verde"
    assert data[1]["name"] == "Pousada Mantiqueira"


def test_filter_establishments_by_category(client: TestClient) -> None:
    create_establishment(client, "Hotel Serra Verde", "hotel")
    create_establishment(client, "Pousada Mantiqueira", "pousada")

    response = client.get(
        BASE_URL,
        params={"category": "hotel"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Hotel Serra Verde"
    assert data[0]["category"] == "hotel"


def test_get_establishment(client: TestClient) -> None:
    establishment = create_establishment(client)

    response = client.get(
        f"{BASE_URL}/{establishment['id']}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == establishment["id"]
    assert response.json()["name"] == establishment["name"]


def test_get_nonexistent_establishment_returns_404(
    client: TestClient,
) -> None:
    response = client.get(f"{BASE_URL}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Tourism establishment not found.",
    }


def test_update_establishment(client: TestClient) -> None:
    establishment = create_establishment(client)

    response = client.put(
        f"{BASE_URL}/{establishment['id']}",
        json={
            "name": "Hotel Serra Azul",
            "category": "resort",
            "is_active": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == establishment["id"]
    assert data["name"] == "Hotel Serra Azul"
    assert data["category"] == "resort"
    assert data["is_active"] is True


def test_deactivate_establishment(client: TestClient) -> None:
    establishment = create_establishment(client)

    response = client.delete(
        f"{BASE_URL}/{establishment['id']}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    get_response = client.get(
        f"{BASE_URL}/{establishment['id']}",
    )

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["is_active"] is False


def test_create_establishment_with_invalid_data_returns_422(
    client: TestClient,
) -> None:
    response = client.post(
        BASE_URL,
        json={
            "name": "",
            "category": "hotel",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
