from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.users import repository
from app.users.exceptions import (
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


def normalize_email(email: str) -> str:
    return email.strip().lower()


def list_users(db: Session) -> list[User]:
    return repository.list_users(db)


def get_user(db: Session, user_id: int) -> User:
    user = repository.get_user_by_id(db, user_id)

    if user is None:
        raise UserNotFoundError

    return user


def create_user(db: Session, data: UserCreate) -> User:
    normalized_email = normalize_email(str(data.email))

    existing_user = repository.get_user_by_email(
        db,
        normalized_email,
    )

    if existing_user is not None:
        raise UserEmailAlreadyExistsError

    user = User(
        name=data.name,
        email=normalized_email,
        password_hash=hash_password(data.password),
        is_active=True,
    )

    try:
        return repository.add_user(db, user)
    except IntegrityError as error:
        db.rollback()
        raise UserEmailAlreadyExistsError from error


def update_user(
    db: Session,
    user_id: int,
    data: UserUpdate,
) -> User:
    user = get_user(db, user_id)
    normalized_email = normalize_email(str(data.email))

    existing_user = repository.get_user_by_email(
        db,
        normalized_email,
    )

    if existing_user is not None and existing_user.id != user.id:
        raise UserEmailAlreadyExistsError

    user.name = data.name
    user.email = normalized_email

    if data.password is not None:
        user.password_hash = hash_password(data.password)

    try:
        return repository.update_user(db, user)
    except IntegrityError as error:
        db.rollback()
        raise UserEmailAlreadyExistsError from error


def activate_user(db: Session, user_id: int) -> User:
    return _set_active(db, user_id, is_active=True)


def deactivate_user(db: Session, user_id: int) -> User:
    return _set_active(db, user_id, is_active=False)


def _set_active(db: Session, user_id: int, *, is_active: bool) -> User:
    user = get_user(db, user_id)

    if user.is_active == is_active:
        return user

    user.is_active = is_active

    return repository.update_user(db, user)
