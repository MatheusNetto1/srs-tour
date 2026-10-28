from sqlalchemy.orm import Session

from app.core.config import settings
from app.users import repository, service
from app.users.models import UserRole
from app.users.schemas import UserCreate


def seed_admin_user(session: Session) -> None:
    if settings.admin_email is None or settings.admin_password is None:
        print("Admin inicial não criado: configure ADMIN_EMAIL e ADMIN_PASSWORD.")
        return

    normalized_email = service.normalize_email(settings.admin_email)
    existing_user = repository.get_user_by_email(session, normalized_email)

    if existing_user is not None:
        if not existing_user.is_active:
            print(
                "Admin inicial não alterado: o e-mail configurado pertence a "
                "um usuário inativo."
            )
        else:
            print("Admin inicial já existe; nenhuma alteração foi feita.")
        return

    admin = service.create_user(
        session,
        UserCreate(
            name="Administrador",
            email=normalized_email,
            password=settings.admin_password,
        ),
    )

    if admin.role != UserRole.ADMIN:
        raise RuntimeError("O usuário inicial não recebeu o papel admin.")
