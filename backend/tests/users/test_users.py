import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.dependencies import get_db
from app.core.security import verify_password
from app.main import app
from app.users.models import User

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


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def create_user(
    client: TestClient,
    *,
    name: str = "Administrador",
    email: str = "admin@example.com",
    password: str = "secure-password",
):
    return client.post(
        "/api/v1/users",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


def test_create_user(client: TestClient) -> None:
    response = create_user(client)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Administrador"
    assert data["email"] == "admin@example.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_user_does_not_expose_password_hash(
    client: TestClient,
) -> None:
    response = create_user(client)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert "password" not in data
    assert "password_hash" not in data


def test_create_user_hashes_password(
    client: TestClient,
) -> None:
    plain_password = "secure-password"

    response = create_user(
        client,
        password=plain_password,
    )

    assert response.status_code == status.HTTP_201_CREATED

    with TestSessionLocal() as db:
        user = db.get(User, response.json()["id"])

        assert user is not None
        assert user.password_hash != plain_password
        assert verify_password(
            plain_password,
            user.password_hash,
        )


def test_create_user_rejects_duplicate_email(
    client: TestClient,
) -> None:
    first_response = create_user(client)
    second_response = create_user(
        client,
        name="Outro administrador",
        email="ADMIN@example.com",
    )

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_409_CONFLICT
    assert second_response.json() == {
        "detail": "Já existe um usuário com este e-mail.",
    }


def test_list_users(client: TestClient) -> None:
    create_user(
        client,
        name="Primeiro usuário",
        email="first@example.com",
    )
    create_user(
        client,
        name="Segundo usuário",
        email="second@example.com",
    )

    response = client.get("/api/v1/users")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Primeiro usuário"
    assert data[1]["name"] == "Segundo usuário"


def test_get_user_by_id(client: TestClient) -> None:
    created_response = create_user(client)
    user_id = created_response.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == user_id
    assert response.json()["email"] == "admin@example.com"


def test_get_nonexistent_user_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Usuário não encontrado.",
    }


def test_update_user(client: TestClient) -> None:
    created_response = create_user(client)
    user_id = created_response.json()["id"]

    response = client.put(
        f"/api/v1/users/{user_id}",
        json={
            "name": "Administrador atualizado",
            "email": "updated@example.com",
            "password": "new-secure-password",
            "is_active": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Administrador atualizado"
    assert data["email"] == "updated@example.com"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_deactivate_user(client: TestClient) -> None:
    created_response = create_user(client)
    user_id = created_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.content == b""

    get_response = client.get(
        f"/api/v1/users/{user_id}",
    )

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["is_active"] is False
