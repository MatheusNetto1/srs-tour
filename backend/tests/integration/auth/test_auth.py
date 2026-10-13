from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.core.config import settings
from app.core.messages import get_message
from app.core.security import create_access_token, hash_password
from app.users.models import User

LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

USER_EMAIL = "admin@srstour.com"
USER_PASSWORD = "senha-segura-123"

INVALID_CREDENTIALS = get_message("auth.invalid_credentials")
INVALID_TOKEN = get_message("auth.invalid_token")


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
) -> Response:
    return client.post(
        LOGIN_URL,
        data={
            "username": email,
            "password": password,
        },
    )


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def encode_token(payload: dict, algorithm: str = settings.algorithm) -> str:
    return jwt.encode(payload, settings.secret_key, algorithm=algorithm)


def expires_in(minutes: int = 30) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=minutes)


def assert_invalid_credentials(response: Response) -> None:
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == INVALID_CREDENTIALS
    assert response.headers["www-authenticate"] == "Bearer"


def assert_invalid_token(response: Response) -> None:
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == INVALID_TOKEN
    assert response.headers["www-authenticate"] == "Bearer"


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

    assert_invalid_credentials(response)


def test_login_with_nonexistent_user_returns_401(
    client: TestClient,
) -> None:
    response = login(client, email="ninguem@srstour.com")

    assert_invalid_credentials(response)


def test_login_with_nonexistent_user_checks_dummy_hash(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checked_hashes: list[str] = []

    def spy_verify_password(password: str, hashed_password: str) -> bool:
        checked_hashes.append(hashed_password)
        return False

    monkeypatch.setattr(auth_service, "verify_password", spy_verify_password)

    response = login(client, email="ninguem@srstour.com")

    assert_invalid_credentials(response)
    assert checked_hashes == [auth_service.get_dummy_password_hash()]


def test_login_with_inactive_user_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session, is_active=False)

    response = login(client)

    assert_invalid_credentials(response)


def test_login_with_password_above_limit_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = login(
        client,
        password="a" * (auth_service.PASSWORD_MAX_LENGTH + 1),
    )

    assert_invalid_credentials(response)


def test_login_without_credentials_returns_422(
    client: TestClient,
) -> None:
    response = client.post(LOGIN_URL, data={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_login_with_json_body_returns_422(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = client.post(
        LOGIN_URL,
        json={
            "username": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )

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


def test_me_identifies_the_token_owner(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)
    other_user = create_user(db_session, email="outro@srstour.com")

    token = login(client, email="outro@srstour.com").json()["access_token"]

    response = client.get(ME_URL, headers=auth_headers(token))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == other_user.id
    assert response.json()["email"] == "outro@srstour.com"


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get(ME_URL)

    assert_invalid_token(response)


def test_me_with_non_bearer_scheme_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)
    token = login(client).json()["access_token"]

    response = client.get(ME_URL, headers={"Authorization": f"Basic {token}"})

    assert_invalid_token(response)


def test_me_with_malformed_token_returns_401(client: TestClient) -> None:
    response = client.get(ME_URL, headers=auth_headers("token-invalido"))

    assert_invalid_token(response)


def test_me_with_token_signed_by_other_key_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = jwt.encode(
        {"sub": str(user.id), "exp": expires_in()},
        "outra-chave-secreta-com-pelo-menos-32-bytes",
        algorithm=settings.algorithm,
    )

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


def test_me_with_token_using_other_algorithm_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = encode_token(
        {"sub": str(user.id), "exp": expires_in()},
        algorithm="HS512",
    )

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


def test_me_with_unsigned_token_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = jwt.encode(
        {"sub": str(user.id), "exp": expires_in()},
        key=None,
        algorithm="none",
    )

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


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

    assert_invalid_token(response)


def test_me_with_token_without_exp_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = encode_token({"sub": str(user.id)})

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


def test_me_with_token_without_sub_returns_401(client: TestClient) -> None:
    token = encode_token({"exp": expires_in()})

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


def test_me_with_non_numeric_sub_returns_401(client: TestClient) -> None:
    token = encode_token({"sub": "admin", "exp": expires_in()})

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


def test_me_with_token_of_nonexistent_user_returns_401(
    client: TestClient,
) -> None:
    token = create_access_token(subject="999999")

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)


def test_me_with_token_of_deactivated_user_returns_401(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    token = login(client).json()["access_token"]

    user.is_active = False
    db_session.commit()

    response = client.get(ME_URL, headers=auth_headers(token))

    assert_invalid_token(response)
