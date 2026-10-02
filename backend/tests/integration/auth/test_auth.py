from datetime import timedelta

import jwt
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.users.models import User

LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

USER_EMAIL = "admin@srstour.com"
USER_PASSWORD = "senha-segura-123"


def create_user(
    db_session: Session,
    email: str = USER_EMAIL,
    password: str = USER_PASSWORD,
    is_active: bool = True,
) -> User:
    user = User(
        name="Administrador",
        email=email,
        password_hash=hash_password(password),
        is_active=is_active,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def login(
    client: TestClient,
    email: str = USER_EMAIL,
    password: str = USER_PASSWORD,
):
    return client.post(
        LOGIN_URL,
        data={
            "username": email,
            "password": password,
        },
    )


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_with_valid_credentials(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)

    response = login(client)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["token_type"] == "bearer"

    payload = jwt.decode(
        data["access_token"],
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert payload["sub"] == str(user.id)


def test_login_normalizes_email(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = login(client, email="  ADMIN@SrsTour.com ")

    assert response.status_code == status.HTTP_200_OK


def test_login_with_wrong_password_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = login(client, password="senha-errada-123")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "E-mail ou senha inválidos."
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_with_nonexistent_user_returns_401(
    client: TestClient,
) -> None:
    response = login(client, email="ninguem@srstour.com")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "E-mail ou senha inválidos."


def test_login_with_inactive_user_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session, is_active=False)

    response = login(client)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "E-mail ou senha inválidos."


def test_login_without_credentials_returns_422(
    client: TestClient,
) -> None:
    response = client.post(LOGIN_URL, data={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_me_with_valid_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = login(client).json()["access_token"]

    response = client.get(ME_URL, headers=auth_headers(token))

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == user.id
    assert data["email"] == USER_EMAIL
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_malformed_token_returns_401(client: TestClient) -> None:
    response = client.get(ME_URL, headers=auth_headers("token-invalido"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Não foi possível validar as credenciais."


def test_me_with_token_signed_by_other_key_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = jwt.encode(
        {"sub": str(user.id)},
        "outra-chave-secreta-com-pelo-menos-32-bytes",
        algorithm=settings.algorithm,
    )

    response = client.get(ME_URL, headers=auth_headers(token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_with_expired_token_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=-1),
    )

    response = client.get(ME_URL, headers=auth_headers(token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_with_token_of_nonexistent_user_returns_401(
    client: TestClient,
) -> None:
    token = create_access_token(subject="999999")

    response = client.get(ME_URL, headers=auth_headers(token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_with_token_of_deactivated_user_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = login(client).json()["access_token"]

    user.is_active = False
    db_session.commit()

    response = client.get(ME_URL, headers=auth_headers(token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
