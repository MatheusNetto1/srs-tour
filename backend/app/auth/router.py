from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import service
from app.auth.dependencies import CurrentUser
from app.auth.schemas import Token
from app.core.dependencies import DbSession
from app.users.models import User
from app.users.schemas import UserResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    try:
        return service.login(db, form_data.username, form_data.password)
    except service.InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(current_user: CurrentUser) -> User:
    return current_user
