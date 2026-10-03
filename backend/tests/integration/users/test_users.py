from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.users.models import User

BASE_URL = "/api/v1/users"

EMAIL_CONFLICT_DETAIL = "Já existe um usuário com este e-mail."
NOT_FOUND_DETAIL = "Usuário não encontrado."


def create_user(
    client: TestClient,
    *,
    name: str = "Administrador",
    email: str = "admin@example.com",
    password: str = "secure-password",
):
    return client.post(
        BASE_URL,
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


def update_payload(**overrides) -> dict:
    payload = {
        "name": "Administrador atualizado",
        "email": "updated@example.com",
    }
    payload.update(overrides)

    return payload


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


def test_create_user_does_not_expose_password_or_hash(
    client: TestClient,
) -> None:
    response = create_user(client)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert "password" not in data
    assert "password_hash" not in data


def test_create_user_hashes_password(
    client: TestClient,
    db_session: Session,
) -> None:
    plain_password = "secure-password"

    response = create_user(client, password=plain_password)

    assert response.status_code == status.HTTP_201_CREATED

    user = db_session.get(User, response.json()["id"])

    assert user is not None
    assert user.password_hash != plain_password
    assert verify_password(plain_password, user.password_hash)


def test_create_user_normalizes_email(
    client: TestClient,
    db_session: Session,
) -> None:
    response = create_user(client, email="  Admin@Example.COM ")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "admin@example.com"

    stored_email = db_session.scalar(select(User.email))

    assert stored_email == "admin@example.com"


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
    assert second_response.json() == {"detail": EMAIL_CONFLICT_DETAIL}


def test_create_user_strips_name(client: TestClient) -> None:
    response = create_user(client, name="  Maria Souza  ")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Maria Souza"


def test_create_user_rejects_invalid_payload(
    client: TestClient,
) -> None:
    invalid_payloads = [
        {"name": "   ", "email": "a@example.com", "password": "secure-password"},
        {"name": "Maria", "email": "not-an-email", "password": "secure-password"},
        {"name": "Maria", "email": "a@example.com", "password": "short"},
    ]

    for payload in invalid_payloads:
        response = client.post(BASE_URL, json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Primeiro usuário"
    assert data[1]["name"] == "Segundo usuário"
    assert all("password_hash" not in user for user in data)


def test_get_user_by_id(client: TestClient) -> None:
    user_id = create_user(client).json()["id"]

    response = client.get(f"{BASE_URL}/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == user_id
    assert response.json()["email"] == "admin@example.com"


def test_get_nonexistent_user_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get(f"{BASE_URL}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_update_user(client: TestClient) -> None:
    user_id = create_user(client).json()["id"]

    response = client.put(
        f"{BASE_URL}/{user_id}",
        json=update_payload(),
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == "Administrador atualizado"
    assert data["email"] == "updated@example.com"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_update_user_with_new_password_generates_new_hash(
    client: TestClient,
    db_session: Session,
) -> None:
    user_id = create_user(client, password="old-secure-password").json()["id"]

    response = client.put(
        f"{BASE_URL}/{user_id}",
        json=update_payload(password="new-secure-password"),
    )

    assert response.status_code == status.HTTP_200_OK

    db_session.expire_all()
    user = db_session.get(User, user_id)

    assert user is not None
    assert verify_password("new-secure-password", user.password_hash)
    assert not verify_password("old-secure-password", user.password_hash)


def test_update_user_without_password_keeps_current_hash(
    client: TestClient,
    db_session: Session,
) -> None:
    user_id = create_user(client, password="old-secure-password").json()["id"]
    original_user = db_session.get(User, user_id)

    assert original_user is not None

    original_hash = original_user.password_hash

    response = client.put(
        f"{BASE_URL}/{user_id}",
        json=update_payload(),
    )

    assert response.status_code == status.HTTP_200_OK

    db_session.expire_all()
    user = db_session.get(User, user_id)

    assert user is not None
    assert user.password_hash == original_hash
    assert verify_password("old-secure-password", user.password_hash)


def test_update_user_normalizes_email(client: TestClient) -> None:
    user_id = create_user(client).json()["id"]

    response = client.put(
        f"{BASE_URL}/{user_id}",
        json=update_payload(email="  Updated@Example.COM "),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "updated@example.com"


def test_update_user_allows_keeping_own_email(
    client: TestClient,
) -> None:
    user_id = create_user(client).json()["id"]

    response = client.put(
        f"{BASE_URL}/{user_id}",
        json=update_payload(email="ADMIN@example.com"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "admin@example.com"


def test_update_user_rejects_email_from_another_user(
    client: TestClient,
) -> None:
    create_user(client, email="first@example.com")
    second_id = create_user(client, email="second@example.com").json()["id"]

    response = client.put(
        f"{BASE_URL}/{second_id}",
        json=update_payload(email="first@example.com"),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EMAIL_CONFLICT_DETAIL}


def test_update_nonexistent_user_returns_not_found(
    client: TestClient,
) -> None:
    response = client.put(
        f"{BASE_URL}/999999",
        json=update_payload(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_deactivate_user(
    client: TestClient,
    db_session: Session,
) -> None:
    user_id = create_user(client).json()["id"]

    delete_response = client.delete(f"{BASE_URL}/{user_id}")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.content == b""

    get_response = client.get(f"{BASE_URL}/{user_id}")

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["is_active"] is False

    db_session.expire_all()

    assert db_session.get(User, user_id) is not None


def test_deactivate_nonexistent_user_returns_not_found(
    client: TestClient,
) -> None:
    response = client.delete(f"{BASE_URL}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_deactivate_already_inactive_user_is_idempotent(
    client: TestClient,
) -> None:
    user_id = create_user(client).json()["id"]

    first_response = client.delete(f"{BASE_URL}/{user_id}")
    second_response = client.delete(f"{BASE_URL}/{user_id}")

    assert first_response.status_code == status.HTTP_204_NO_CONTENT
    assert second_response.status_code == status.HTTP_204_NO_CONTENT


def test_update_user_cannot_change_active_state(
    client: TestClient,
) -> None:
    active_id = create_user(client, email="active@example.com").json()["id"]
    inactive_id = create_user(client, email="inactive@example.com").json()["id"]
    client.delete(f"{BASE_URL}/{inactive_id}")

    deactivate_attempt = client.put(
        f"{BASE_URL}/{active_id}",
        json=update_payload(email="active@example.com", is_active=False),
    )
    activate_attempt = client.put(
        f"{BASE_URL}/{inactive_id}",
        json=update_payload(email="inactive@example.com", is_active=True),
    )

    assert deactivate_attempt.status_code == status.HTTP_200_OK
    assert deactivate_attempt.json()["is_active"] is True
    assert activate_attempt.status_code == status.HTTP_200_OK
    assert activate_attempt.json()["is_active"] is False


def test_activate_inactive_user(client: TestClient) -> None:
    user_id = create_user(client).json()["id"]
    client.delete(f"{BASE_URL}/{user_id}")

    response = client.post(f"{BASE_URL}/{user_id}/activate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is True
    assert client.get(f"{BASE_URL}/{user_id}").json()["is_active"] is True


def test_activate_active_user_is_idempotent(
    client: TestClient,
) -> None:
    user_id = create_user(client).json()["id"]

    first_response = client.post(f"{BASE_URL}/{user_id}/activate")
    second_response = client.post(f"{BASE_URL}/{user_id}/activate")

    assert first_response.status_code == status.HTTP_200_OK
    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.json()["is_active"] is True


def test_activate_nonexistent_user_returns_not_found(
    client: TestClient,
) -> None:
    response = client.post(f"{BASE_URL}/999999/activate")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": NOT_FOUND_DETAIL}


def test_activate_user_does_not_change_other_data(
    client: TestClient,
    db_session: Session,
) -> None:
    user_id = create_user(
        client,
        name="Maria Souza",
        email="maria@example.com",
    ).json()["id"]
    client.delete(f"{BASE_URL}/{user_id}")

    db_session.expire_all()
    inactive_user = db_session.get(User, user_id)

    assert inactive_user is not None

    password_hash = inactive_user.password_hash

    response = client.post(f"{BASE_URL}/{user_id}/activate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Maria Souza"
    assert response.json()["email"] == "maria@example.com"

    db_session.expire_all()
    user = db_session.get(User, user_id)

    assert user is not None
    assert user.password_hash == password_hash


def test_list_users_includes_inactive_users(
    client: TestClient,
) -> None:
    active_id = create_user(client, email="active@example.com").json()["id"]
    inactive_id = create_user(client, email="inactive@example.com").json()["id"]
    client.delete(f"{BASE_URL}/{inactive_id}")

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK

    states = {user["id"]: user["is_active"] for user in response.json()}

    assert states == {active_id: True, inactive_id: False}


def test_get_inactive_user_by_id(client: TestClient) -> None:
    user_id = create_user(client).json()["id"]
    client.delete(f"{BASE_URL}/{user_id}")

    response = client.get(f"{BASE_URL}/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == user_id
    assert response.json()["is_active"] is False


def test_inactive_user_keeps_email_reserved_on_create(
    client: TestClient,
) -> None:
    user_id = create_user(client, email="admin@example.com").json()["id"]
    client.delete(f"{BASE_URL}/{user_id}")

    response = create_user(client, email="ADMIN@Example.com")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EMAIL_CONFLICT_DETAIL}


def test_inactive_user_keeps_email_reserved_on_update(
    client: TestClient,
) -> None:
    inactive_id = create_user(client, email="inactive@example.com").json()["id"]
    client.delete(f"{BASE_URL}/{inactive_id}")
    other_id = create_user(client, email="other@example.com").json()["id"]

    response = client.put(
        f"{BASE_URL}/{other_id}",
        json=update_payload(email="INACTIVE@example.com"),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EMAIL_CONFLICT_DETAIL}


def test_database_rejects_emails_that_differ_only_by_case(
    db_session: Session,
) -> None:
    insert = text(
        "INSERT INTO users (name, email, password_hash) VALUES (:name, :email, 'hash')"
    )

    db_session.execute(insert, {"name": "Primeiro", "email": "User@Example.com"})
    db_session.commit()

    try:
        db_session.execute(
            insert,
            {"name": "Segundo", "email": "user@example.com"},
        )
        db_session.commit()
    except IntegrityError as error:
        db_session.rollback()

        assert "uq_users_email_lower" in str(error.orig)
    else:
        raise AssertionError("Expected the database to reject the duplicate e-mail.")
