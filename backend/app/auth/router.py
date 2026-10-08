from typing import Annotated

from fastapi import APIRouter, Depends
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
    return service.login(db, form_data.username, form_data.password)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(current_user: CurrentUser) -> User:
    return current_user
