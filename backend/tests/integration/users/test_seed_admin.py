from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.users.models import User, UserRole
from scripts.seed_admin import seed_admin_user

ADMIN_EMAIL = "admin-seed@example.com"
ADMIN_PASSWORD = "admin-password-123"


def test_seed_admin_is_idempotent(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email", f"  {ADMIN_EMAIL.upper()}  ")
    monkeypatch.setattr(settings, "admin_password", ADMIN_PASSWORD)

    seed_admin_user(db_session)
    seed_admin_user(db_session)

    users_count = db_session.scalar(select(func.count()).select_from(User))
    admin = db_session.scalar(select(User).where(User.email == ADMIN_EMAIL))

    assert users_count == 1
    assert admin is not None
    assert admin.role == UserRole.ADMIN
    assert admin.is_active is True
    assert verify_password(ADMIN_PASSWORD, admin.password_hash)


def test_seed_admin_does_not_reactivate_inactive_user(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email", ADMIN_EMAIL)
    monkeypatch.setattr(settings, "admin_password", ADMIN_PASSWORD)

    seed_admin_user(db_session)
    admin = db_session.scalar(select(User).where(User.email == ADMIN_EMAIL))

    assert admin is not None

    admin.is_active = False
    db_session.commit()

    seed_admin_user(db_session)
    db_session.expire_all()

    inactive_admin = db_session.scalar(select(User).where(User.email == ADMIN_EMAIL))

    assert inactive_admin is not None
    assert inactive_admin.is_active is False
