import jwt
from sqlalchemy.orm import Session

from app.auth.schemas import Token
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.users import repository as users_repository
from app.users.models import User
from app.users.service import normalize_email

# Hash usado quando o e-mail não existe, para que o tempo de resposta
# não revele quais e-mails estão cadastrados.
DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing")


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    user = users_repository.get_user_by_email(
        db,
        normalize_email(email),
    )

    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
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


def get_user_from_token(db: Session, token: str) -> User:
    user_id = decode_access_token(token)

    user = users_repository.get_user_by_id(db, user_id)

    if user is None or not user.is_active:
        raise InvalidTokenError

    return user
