from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


def list_users(db: Session) -> list[User]:
    statement = select(User).order_by(User.name)

    return list(db.scalars(statement).all())


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)

    return db.scalar(statement)


def add_user(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    db.refresh(user)

    return user


def update_user(db: Session, user: User) -> User:
    db.flush()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.flush()
