from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.users import repository
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


class UserNotFoundError(Exception):
    pass


class UserEmailAlreadyExistsError(Exception):
    pass


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
        name=data.name.strip(),
        email=normalized_email,
        password_hash=hash_password(data.password),
        is_active=True,
    )

    try:
        repository.add_user(db, user)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise UserEmailAlreadyExistsError from error

    return user


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

    user.name = data.name.strip()
    user.email = normalized_email
    user.is_active = data.is_active

    if data.password is not None:
        user.password_hash = hash_password(data.password)

    try:
        repository.update_user(db, user)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise UserEmailAlreadyExistsError from error

    return user


def deactivate_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)

    user.is_active = False

    repository.update_user(db, user)
    db.commit()
