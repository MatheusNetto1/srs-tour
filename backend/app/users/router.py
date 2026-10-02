from fastapi import APIRouter, HTTPException, Response, status

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
    try:
        return service.get_user(db, user_id)
    except service.UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        ) from error


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: DbSession,
) -> User:
    try:
        return service.create_user(db, data)
    except service.UserEmailAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail.",
        ) from error


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: DbSession,
) -> User:
    try:
        return service.update_user(db, user_id, data)
    except service.UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        ) from error
    except service.UserEmailAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail.",
        ) from error


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_user(
    user_id: int,
    db: DbSession,
) -> Response:
    try:
        service.deactivate_user(db, user_id)
    except service.UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)
