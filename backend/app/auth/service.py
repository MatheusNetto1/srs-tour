from functools import lru_cache

import jwt
from sqlalchemy.orm import Session

from app.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from app.auth.schemas import Token
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.users import repository as users_repository
from app.users.models import User
from app.users.service import normalize_email

# Mesmo teto de UserCreate: senhas maiores nunca foram cadastradas, e recusá-las
# antes do argon2 evita gastar CPU com corpos enormes.
PASSWORD_MAX_LENGTH = 128


@lru_cache
def get_dummy_password_hash() -> str:
    # Hash usado quando o e-mail não existe, para que o tempo de resposta
    # não revele quais e-mails estão cadastrados.
    return hash_password("dummy-password-for-timing")


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    if len(password) > PASSWORD_MAX_LENGTH:
        raise InvalidCredentialsError

    user = users_repository.get_user_by_email(
        db,
        normalize_email(email),
    )

    if user is None:
        verify_password(password, get_dummy_password_hash())
        raise InvalidCredentialsError

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    if not user.is_active:
        raise InvalidCredentialsError

    return user


def login(
    db: Session,
    email: str,
    password: str,
) -> Token:
    user = authenticate_user(db, email, password)

    return Token(
        access_token=create_access_token(subject=str(user.id)),
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as error:
        raise InvalidTokenError from error

    try:
        return int(payload["sub"])
    except (TypeError, ValueError) as error:
        raise InvalidTokenError from error


def get_user_from_token(db: Session, token: str | None) -> User:
    if token is None:
        raise InvalidTokenError

    user_id = decode_access_token(token)

    user = users_repository.get_user_by_id(db, user_id)

    if user is None or not user.is_active:
        raise InvalidTokenError

    return user
