from fastapi import APIRouter, Response, status

from app.core.dependencies import DbSession
from app.users import service
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(db: DbSession) -> list[User]:
    return service.list_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: DbSession,
) -> User:
    return service.get_user(db, user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: DbSession,
) -> User:
    return service.create_user(db, data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: DbSession,
) -> User:
    return service.update_user(db, user_id, data)


@router.post(
    "/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user(
    user_id: int,
    db: DbSession,
) -> User:
    return service.activate_user(db, user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_user(
    user_id: int,
    db: DbSession,
) -> Response:
    service.deactivate_user(db, user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
